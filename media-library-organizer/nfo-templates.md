# NFO 模板

Use this file only when generating NFO content. It does not decide whether a file should be renamed, moved, or downloaded.

## movie.nfo

```xml
<movie>
  <title>阿凡达</title>
  <originaltitle>Avatar</originaltitle>
  <sorttitle>阿凡达</sorttitle>
  <year>2009</year>
  <premiered>2009-12-18</premiered>
  <country>美国</country>
  <language>英语</language>
  <plot>简介...</plot>
  <mpaa>PG-13</mpaa>
  <genre>科幻</genre>
  <tag>冒险</tag>
  <actor><name>Sam Worthington</name></actor>
  <director>James Cameron</director>
  <fileinfo>
    <streamdetails>
      <video><codec>hevc</codec><aspect>1.78</aspect><width>3840</width><height>2160</height></video>
      <audio><codec>eac3</codec><channels>8</channels></audio>
    </streamdetails>
  </fileinfo>
</movie>
```

## tvshow.nfo

```xml
<tvshow>
  <title>五十公里桃花坞</title>
  <originaltitle>Wonderland</originaltitle>
  <sorttitle>五十公里桃花坞</sorttitle>
  <year>2021</year>
  <premiered>2021-05-23</premiered>
  <country>中国</country>
  <language>汉语普通话</language>
  <plot>简介...</plot>
  <tagline>一个人抵达&#xFF0C;一群人出发</tagline>
  <status>Returning Series</status>
  <mpaa>TV-Y7</mpaa>
  <studio>腾讯视频</studio>
  <genre>真人秀</genre>
  <tag>真人秀</tag>
  <tag>社会实验</tag>
  <actor><name>演员名</name></actor>
  <director>导演名</director>
  <credits>主创名</credits>
</tvshow>
```

## episodedetails.nfo

```xml
<episodedetails>
  <title>初见面</title>
  <season>1</season>
  <episode>1</episode>
  <aired>2021-05-23</aired>
  <plot>简介...</plot>
  <showtitle>五十公里桃花坞</showtitle>
  <thumb>/path/to/thumb.jpg</thumb>
</episodedetails>
```

## season.nfo

```xml
<season>
  <seasonnumber>1</seasonnumber>
  <title>第一季</title>
  <plot>本季剧情简介...</plot>
  <premiered>2015-06-14</premiered>
</season>
```
