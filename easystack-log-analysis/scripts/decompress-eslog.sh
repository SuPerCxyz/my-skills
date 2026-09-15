#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: bash decompress-eslog.sh [--input PATH] [--output DIR]

PATH may be one .eslog file or a directory containing top-level .eslog files.
With no arguments, input and output default to the current working directory.
For an explicit input file, output defaults to its parent directory; for an input directory,
output defaults to that directory. --output overrides the default.
Every .log.gz file is expanded to a readable .log file. The original .log.gz is kept.
A cross-platform components/ view is built from copied .log files; larger files win name conflicts.
EOF
}

input_path=$PWD
output_dir=$PWD
output_explicit=false
password=${ESLOG_PASSWORD:-easycloud}
while (($#)); do
    case "$1" in
        --input)
            input_path=${2:?missing value for --input}
            shift 2
            ;;
        --output)
            output_dir=${2:?missing value for --output}
            output_explicit=true
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

for command in awk cp df dirname find gzip mktemp mv realpath sort tar unzip wc; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "Required command not found: $command" >&2
        exit 1
    }
done

declare -a bundles=()
if [[ -f $input_path ]]; then
    [[ $input_path == *.eslog ]] || {
        echo "Input file must end with .eslog: $input_path" >&2
        exit 2
    }
    bundles+=("$(realpath -- "$input_path")")
    [[ $output_explicit == true ]] || output_dir=$(dirname -- "${bundles[0]}")
elif [[ -d $input_path ]]; then
    input_path=$(realpath -- "$input_path")
    while IFS= read -r -d '' bundle; do
        bundles+=("$bundle")
    done < <(find "$input_path" -maxdepth 1 -type f -name '*.eslog' -print0 | sort -z)
    [[ $output_explicit == true ]] || output_dir=$input_path
else
    echo "Input path does not exist: $input_path" >&2
    exit 2
fi

((${#bundles[@]})) || {
    echo "No top-level .eslog files found under: $input_path" >&2
    exit 1
}

mkdir -p -- "$output_dir"
output_dir=$(realpath -- "$output_dir")

validate_tar_listing() {
    local archive_label=$1 entry normalized top_level
    while IFS= read -r entry; do
        case "$entry" in
            /*|../*|*/../*|*/..)
                echo "Unsafe path in tar archive $archive_label: $entry" >&2
                return 1
                ;;
        esac
        normalized=$entry
        while [[ $normalized == ./* ]]; do
            normalized=${normalized#./}
        done
        [[ -z $normalized || $normalized == . ]] && continue
        top_level=${normalized%%/*}
        case "$top_level" in
            ecs.*) ;;
            *)
                echo "Unexpected top-level path in tar archive $archive_label: $entry" >&2
                return 1
                ;;
        esac
    done
}

preflight_log_space() {
    local destination=$1 log_gz bytes required=0 available reserve=$((16 * 1024 * 1024))
    while IFS= read -r -d '' log_gz; do
        bytes=$(LC_ALL=C gzip -l -- "$log_gz" | awk 'NR == 2 {print $2}')
        [[ $bytes =~ ^[0-9]+$ ]] || {
            echo "Cannot determine expanded size: $log_gz" >&2
            return 1
        }
        required=$((required + bytes))
    done < <(find "$destination" -type f -name '*.log.gz' -print0)
    available=$(df -Pk -- "$destination" | awk 'END {printf "%.0f", $4 * 1024}')
    [[ $available =~ ^[0-9]+$ ]] || {
        echo "Cannot determine available space: $destination" >&2
        return 1
    }
    if ((available < required + reserve)); then
        echo "Insufficient space for log expansion under $destination: required=$((required + reserve)) available=$available" >&2
        return 1
    fi
}

expand_log_atomic() {
    local log_gz=$1 log_path part
    log_path=${log_gz%.gz}
    part=$log_path.part.$$
    partial_logs+=("$part")
    gzip -cd -- "$log_gz" >"$part"
    mv -f -- "$part" "$log_path"
}

process_bundle() (
    local bundle=$1 archive_work archive_root nested_entry nested_archive
    local tar_entry listing entry normalized output_name destination log_gz
    local index=0 tar_index=0 status

    declare -a nested_entries=() tar_entries=() output_order=() partial_logs=()
    declare -A output_names=() output_actions=()

    cleanup() {
        status=$?
        trap - EXIT
        for log_part in "${partial_logs[@]}"; do
            rm -f -- "$log_part"
        done
        rm -rf -- "$archive_work"
        exit "$status"
    }

    archive_root=${TMPDIR:-/var/tmp}
    if [[ ! -d $archive_root || ! -w $archive_root ]]; then
        archive_root=$output_dir
    fi
    archive_work=$(mktemp -d "$archive_root/easystack-eslog-archives.XXXXXX")
    trap cleanup EXIT

    echo "Extracting bundle: $bundle"
    while IFS= read -r nested_entry; do
        case "$nested_entry" in *.eslog.[0-9]*) nested_entries+=("$nested_entry");; esac
    done < <(unzip -Z1 "$bundle")
    ((${#nested_entries[@]})) || {
        echo "No nested .eslog.N entries found in: $bundle" >&2
        exit 1
    }

    for nested_entry in "${nested_entries[@]}"; do
        nested_archive=$archive_work/nested-$index.zip
        unzip -P "$password" -p "$bundle" "$nested_entry" >"$nested_archive"
        tar_entries=()
        while IFS= read -r tar_entry; do
            base_name=${tar_entry##*/}
            case "$base_name" in ecs*.tar) tar_entries+=("$tar_entry");; esac
        done < <(unzip -Z1 "$nested_archive")
        ((${#tar_entries[@]})) || {
            echo "No ecs*.tar entry found in: $nested_entry" >&2
            exit 1
        }

        for tar_entry in "${tar_entries[@]}"; do
            listing=$archive_work/listing-$tar_index.txt
            unzip -p "$nested_archive" "$tar_entry" | tar -tf - >"$listing"
            validate_tar_listing "$tar_entry" <"$listing"

            while IFS= read -r entry; do
                normalized=$entry
                while [[ $normalized == ./* ]]; do
                    normalized=${normalized#./}
                done
                [[ -z $normalized || $normalized == . ]] && continue
                output_name=${normalized%%/*}
                [[ -n ${output_names[$output_name]+x} ]] && continue

                destination=$output_dir/$output_name
                [[ ! -L $destination && ( ! -e $destination || -d $destination ) ]] || {
                    echo "Output path is not a mergeable directory: $destination" >&2
                    exit 1
                }
                output_names[$output_name]=1
                output_order+=("$output_name")
                if [[ -d $destination ]]; then
                    output_actions[$output_name]=Updated
                else
                    output_actions[$output_name]=Created
                fi
            done <"$listing"

            unzip -p "$nested_archive" "$tar_entry" |
                tar --overwrite -xf - -C "$output_dir"
            rm -f -- "$listing"
            tar_index=$((tar_index + 1))
        done
        rm -f -- "$nested_archive"
        index=$((index + 1))
    done

    ((${#output_order[@]})) || {
        echo "No ecs.* directories were extracted from: $bundle" >&2
        exit 1
    }

    for output_name in "${output_order[@]}"; do
        destination=$output_dir/$output_name
        preflight_log_space "$destination"
        while IFS= read -r -d '' log_gz; do
            expand_log_atomic "$log_gz"
        done < <(find "$destination" -type f -name '*.log.gz' -print0)
    done

    for output_name in "${output_order[@]}"; do
        echo "${output_actions[$output_name]}: $output_dir/$output_name"
    done
)

for bundle in "${bundles[@]}"; do
    process_bundle "$bundle"
done

build_component_view() (
    local source_root components_root log_path relative target_dir target_path
    local source_size target_size part copied=0 skipped=0
    local growth=0 max_replacement=0 required available reserve=$((16 * 1024 * 1024))
    declare -a component_parts=()
    declare -A candidate_paths=() candidate_sizes=()
    components_root=$output_dir/components
    cleanup_component_parts() {
        local status=$?
        trap - EXIT
        for part in "${component_parts[@]}"; do
            rm -f -- "$part"
        done
        exit "$status"
    }
    trap cleanup_component_parts EXIT
    [[ ! -L $components_root && ( ! -e $components_root || -d $components_root ) ]] || {
        echo "Component view path is not a directory: $components_root" >&2
        return 1
    }

    while IFS= read -r -d '' source_root; do
        while IFS= read -r -d '' log_path; do
            relative=${log_path#"$source_root"/}
            source_size=$(wc -c <"$log_path")
            if [[ -z ${candidate_sizes[$relative]+x} ]] ||
                ((source_size > candidate_sizes[$relative])); then
                candidate_paths[$relative]=$log_path
                candidate_sizes[$relative]=$source_size
            fi
        done < <(find "$source_root" -type f -name '*.log' -print0)
    done < <(find "$output_dir" -mindepth 1 -maxdepth 1 -type d -name 'ecs.*' -print0 | sort -z)

    for relative in "${!candidate_paths[@]}"; do
        target_path=$components_root/$relative
        source_size=${candidate_sizes[$relative]}
        [[ ! -e $target_path || -f $target_path || -L $target_path ]] || {
            echo "Component target is not a replaceable file: $target_path" >&2
            return 1
        }
        if [[ -f $target_path && ! -L $target_path ]]; then
            target_size=$(wc -c <"$target_path")
            if ((source_size > target_size)); then
                growth=$((growth + source_size - target_size))
                ((source_size > max_replacement)) && max_replacement=$source_size
            fi
        else
            growth=$((growth + source_size))
        fi
    done
    required=$((growth + max_replacement + reserve))
    available=$(df -Pk -- "$output_dir" | awk 'END {printf "%.0f", $4 * 1024}')
    if ((available < required)); then
        echo "Insufficient space for component view under $components_root: required=$required available=$available" >&2
        return 1
    fi

    mkdir -p -- "$components_root"
    for relative in "${!candidate_paths[@]}"; do
        log_path=${candidate_paths[$relative]}
        source_size=${candidate_sizes[$relative]}
        target_path=$components_root/$relative
        target_dir=${target_path%/*}
        mkdir -p -- "$target_dir"

        if [[ -f $target_path && ! -L $target_path ]]; then
            target_size=$(wc -c <"$target_path")
            if ((source_size <= target_size)); then
                skipped=$((skipped + 1))
                continue
            fi
        fi

        part=$target_path.part.$$
        component_parts+=("$part")
        if ! cp -- "$log_path" "$part"; then
            return 1
        fi
        if ! mv -fT -- "$part" "$target_path"; then
            return 1
        fi
        copied=$((copied + 1))
    done

    echo "Component view: $components_root (copied=$copied skipped=$skipped)"
)

build_component_view
