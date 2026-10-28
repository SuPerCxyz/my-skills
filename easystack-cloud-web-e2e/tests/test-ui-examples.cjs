const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const skill = path.resolve(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(skill, file), 'utf8');
const markedCode = (file, name) => read(file).match(new RegExp(`<!-- ${name}:start -->\\s*\x60\x60\x60javascript\\n([\\s\\S]*?)\x60\x60\x60\\s*<!-- ${name}:end -->`))[1];

// The fixture supplies DOM observations and click effects; the code under test
// is extracted unchanged from the actual documentation.
function row(name, project, id, options = {}) {
  const input = { checked: Boolean(options.selected) };
  const control = { clicks: 0, getAttribute: () => options.disabled ? 'true' : null,
    click() { this.clicks++; if (options.selectionWorks !== false) input.checked = true; } };
  const cell = (text) => ({ innerText: text, querySelector: () => null });
  const cells = [cell(name), cell(`${options.domain || 'default'}\n${project}`), cell(id || '')];
  if (options.projectHref) cells[1].querySelector = () => ({ getAttribute: () => options.projectHref });
  return { input, control, cells, getAttribute: () => null,
    querySelectorAll: (selector) => selector === 'td' ? cells : [],
    querySelector: (selector) => selector === 'input[type="checkbox"]' ? input : control };
}

function table(rows) {
  return { rows, getClientRects: () => [1], querySelectorAll(selector) {
    if (selector === 'thead th') return ['Name', 'Domain / Project', 'ID'].map(innerText => ({ innerText }));
    if (selector === '.ant-table-tbody tr') return this.rows;
    return [];
  } };
}

function button(label, options = {}) {
  return { innerText: label, disabled: Boolean(options.disabled), clicks: 0,
    getAttribute: () => null, getClientRects: () => options.hidden ? [] : [1],
    click() { this.clicks++; } };
}

function environment(rows = [], buttons = [], project = 'project-a') {
  const grid = table(rows);
  const current = { innerText: project, click() {} };
  const document = { querySelector: () => current, querySelectorAll(selector) {
    if (selector === '.ant-table') return [grid];
    if (selector === 'button') return buttons;
    return [];
  } };
  const context = vm.createContext({ document, setTimeout, clearTimeout, Date, readSelectionCount: () => grid.rows.filter(item => item.input.checked).length, location: { href: 'https://example.invalid/list' } });
  vm.runInContext(markedCode('interactions.md', 'resource-contract') + '\nglobalThis.api = {resolveResource, resourceIdentity, resourceSelected, selectOnlyResource, actionButton, resourceTable};', context);
  return { grid, current, document, context, readSelectionCount: context.readSelectionCount, ...context.api };
}

test('exact name, project and UUID distinguish prefixes and duplicate names', () => {
  const a = row('vol-10', 'project-a', 'ten');
  const b = row('vol-1', 'project-b', 'other-project');
  const c = row('vol-1', 'project-a', 'one');
  const env = environment([a, b, c]);
  assert.equal(env.resolveResource(env.grid, { name: 'vol-1', project: 'project-a', domain: 'default' }).row, c);
  env.grid.rows.push(row('vol-1', 'project-a', 'duplicate'));
  assert.throws(() => env.resolveResource(env.grid, { name: 'vol-1', project: 'project-a', domain: 'default' }), /ambiguous_resource/);
  assert.equal(env.resolveResource(env.grid, { name: 'vol-1', project: 'project-a', domain: 'default', id: 'one' }).row, c);
  assert.throws(() => env.resolveResource(env.grid, { name: 'vol-1', project: 'project-a', domain: 'default', id: 'missing' }), /resource_not_found/);
});

test('missing identity and wrong current project fail without selecting anything', () => {
  const target = row('vm', 'project-a', null);
  const env = environment([target]);
  assert.throws(() => env.resolveResource(env.grid, { name: 'vm', project: 'project-a', domain: 'default', id: 'required-uuid' }), /resource_not_found/);
  assert.throws(() => env.resolveResource(env.grid, { name: 'vm' }), /resource_identity_required/);
  env.current.innerText = 'project-b';
  assert.throws(() => env.resolveResource(env.grid, { name: 'vm', project: 'project-a', domain: 'default' }), /project_mismatch/);
  assert.equal(target.control.clicks, 0);
});

test('selection is idempotent, rejects other selections, stale rows and failed clicks', async () => {
  const target = row('vm', 'project-a', 'id', { selected: true });
  const env = environment([target]);
  await env.selectOnlyResource(env.grid, target, env.readSelectionCount);
  assert.equal(target.control.clicks, 0);
  env.grid.rows.push(row('other', 'project-a', 'other', { selected: true }));
  await assert.rejects(env.selectOnlyResource(env.grid, target, env.readSelectionCount), /other_resources_selected/);
  env.grid.rows = [];
  await assert.rejects(env.selectOnlyResource(env.grid, target, env.readSelectionCount), /resource_row_stale/);
  const failed = row('failed', 'project-a', 'failed', { selectionWorks: false });
  env.grid.rows = [failed];
  await assert.rejects(env.selectOnlyResource(env.grid, failed, env.readSelectionCount, 0), /selection_unconfirmed/);
  await assert.rejects(env.selectOnlyResource(env.grid, failed, env.readSelectionCount, Infinity), /invalid_timeout/);
});

test('actions map to actual labels and reject hidden, disabled, unknown or ambiguous controls', () => {
  const shutoff = button('Shutoff');
  const allocate = button('Apply For IP To Project');
  const env = environment([], [shutoff, allocate, button('Reboot', { hidden: true })]);
  assert.equal(env.actionButton(env.document, 'stop'), shutoff);
  assert.equal(env.actionButton(env.document, 'allocate_floating_ip'), allocate);
  assert.throws(() => env.actionButton(env.document, 'reboot'), /action_unavailable_or_ambiguous/);
  assert.throws(() => env.actionButton(env.document, 'erase'), /unsupported_action/);
  shutoff.disabled = true;
  assert.throws(() => env.actionButton(env.document, 'stop'), /action_unavailable_or_ambiguous/);
  shutoff.disabled = false;
  env.document.querySelectorAll = () => [shutoff, button('Shutoff')];
  assert.throws(() => env.actionButton(env.document, 'stop'), /action_unavailable_or_ambiguous/);
});

test('the actual delete example returns a pending menu, never terminal success', async () => {
  const target = row('<instance-name>', '<project-name>', 'actual-id', { domain: '<domain-name>' });
  const more = button('More');
  const env = environment([target], [more], '<project-name>');
  const code = read('patterns/instance-ops/delete-instance.md').match(/```js\n([\s\S]*?)```/)[1];
  const result = await vm.runInContext(code, env.context);
  assert.equal(result.ok, null);
  assert.equal(result.terminal, false);
  assert.equal(result.submitted, false);
  assert.equal(target.input.checked, true);
  assert.equal(more.clicks, 1);
  env.document.querySelectorAll = selector => selector === '.ant-table' ? [env.grid] : [];
  const failed = await vm.runInContext(code, env.context);
  assert.equal(failed.ok, false);
  assert.equal(failed.status, 'interaction_failed');
});

function projectEnvironment(onClick) {
  const current = { innerText: 'before', click() {} };
  const option = { innerText: 'after', getClientRects: () => [1], click() { onClick(current); } };
  const document = { querySelector: () => current, querySelectorAll: () => [option] };
  const context = vm.createContext({ document, setTimeout, clearTimeout, Date });
  vm.runInContext(markedCode('connection.md', 'project-contract') + '\nglobalThis.switchProject = switchProject;', context);
  return { current, switchProject: context.switchProject };
}

test('project switch waits for the observed label and asynchronous resource context', async () => {
  let ready = false;
  const env = projectEnvironment(current => {
    setTimeout(() => { current.innerText = 'after'; }, 5);
    setTimeout(() => { ready = true; }, 15);
  });
  const pending = env.switchProject('after', async () => ready, 300);
  assert.equal(env.current.innerText, 'before');
  const result = await pending;
  assert.equal(result.ok, true);
  assert.equal(result.project, 'after');
  assert.equal(ready, true);
});

test('unconfirmed project context stays pending and reports the observed project', async () => {
  const env = projectEnvironment(() => {});
  const result = await env.switchProject('after', () => false, 1);
  assert.equal(result.ok, null);
  assert.equal(result.terminal, false);
  assert.equal(result.submitted, true);
  assert.equal(result.project, 'before');
  const noProbe = await env.switchProject('after', null);
  assert.equal(noProbe.ok, false);
  assert.equal(noProbe.submitted, false);
  const unbounded = await env.switchProject('after', () => true, Infinity);
  assert.equal(unbounded.status, 'invalid_timeout');
});

test('project changes during an awaited probe cannot become successful', async () => {
  const env = projectEnvironment(current => { current.innerText = 'after'; });
  const result = await env.switchProject('after', async () => {
    env.current.innerText = 'third';
    return true;
  }, 5);
  assert.equal(result.ok, null);
  assert.equal(result.project, 'third');
});

test('truthy probe objects and a never-settling probe cannot bypass confirmation or timeout', async () => {
  const env = projectEnvironment(current => { current.innerText = 'after'; });
  const truthy = await env.switchProject('after', () => ({ ok: false }), 5);
  assert.equal(truthy.ok, null);
  const result = await Promise.race([
    env.switchProject('after', () => new Promise(() => {}), 5),
    new Promise(resolve => setTimeout(() => resolve('unbounded'), 100))
  ]);
  assert.notEqual(result, 'unbounded');
  assert.equal(result.ok, null);
});

test('recycled rows and detached tables invalidate selection before any action', async () => {
  const target = row('vm', 'project-a', 'original');
  const env = environment([target]);
  target.control.click = () => { target.input.checked = true; target.cells[0].innerText = 'other'; };
  await assert.rejects(env.selectOnlyResource(env.grid, target, env.readSelectionCount), /identity_changed/);
  target.cells[0].innerText = 'vm';
  env.document.querySelectorAll = selector => selector === '.ant-table' ? [table([])] : [];
  await assert.rejects(env.selectOnlyResource(env.grid, target, () => 1), /table_stale/);
});

test('hidden selections on another page and unobservable selection counts stop bulk actions', async () => {
  const target = row('vm', 'project-a', 'id', { selected: true });
  const env = environment([target]);
  await assert.rejects(env.selectOnlyResource(env.grid, target, () => 2), /other_resources_selected/);
  await assert.rejects(env.selectOnlyResource(env.grid, target), /global_selection_probe_required/);
});

test('same display project in different domains and 32/36-character project IDs stay distinct', () => {
  const compactId = '1234567890abcdef1234567890abcdef';
  const uuid = '12345678-1234-1234-1234-123456789abc';
  const a = row('vm', 'project-a', 'a', { domain: 'domain-a', projectHref: `/projects/${compactId}` });
  const b = row('vm', 'project-a', 'b', { domain: 'domain-b', projectHref: `/projects/${uuid}` });
  const env = environment([a, b]);
  assert.equal(env.resolveResource(env.grid, { name: 'vm', project: 'project-a', domain: 'domain-b' }).row, b);
  assert.equal(env.resolveResource(env.grid, { name: 'vm', project: 'project-a', projectId: compactId }).row, a);
  assert.equal(env.resolveResource(env.grid, { name: 'vm', project: 'project-a', projectId: uuid }).row, b);
  a.cells[1].querySelector = () => ({ getAttribute: () => `/projects/${compactId}dead` });
  assert.throws(() => env.resolveResource(env.grid, { name: 'vm', project: 'project-a', projectId: compactId }), /resource_not_found/);
});

test('project dropdown may load asynchronously and probe rejection preserves submission state', async () => {
  let available = false;
  // Extract a fresh document context so discovery itself is delayed.
  const current = { innerText: 'before', click() {} };
  const choice = { innerText: 'after', getClientRects: () => [1], click() { current.innerText = 'after'; } };
  const document = { querySelector: () => current, querySelectorAll: () => available ? [choice] : [] };
  const context = vm.createContext({ document, setTimeout, clearTimeout, Date });
  vm.runInContext(markedCode('connection.md', 'project-contract') + '\nglobalThis.switchProject = switchProject;', context);
  setTimeout(() => { available = true; }, 5);
  const result = await context.switchProject('after', () => true, 200);
  assert.equal(result.ok, true);
  current.innerText = 'before';
  const failed = await context.switchProject('after', async () => { throw new Error('probe failed'); }, 200);
  assert.equal(failed.ok, false);
  assert.equal(failed.submitted, true);
  assert.equal(failed.status, 'project_probe_failed');
});

test('all documented JavaScript examples have valid syntax', () => {
  function inspect(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) inspect(file);
      else if (entry.name.endsWith('.md')) {
        for (const match of fs.readFileSync(file, 'utf8').matchAll(/```(?:js|javascript)\n([\s\S]*?)```/g)) {
          assert.doesNotThrow(() => new vm.Script(`(async () => {\n${match[1]}\n})()`), file);
        }
      }
    }
  }
  inspect(skill);
});

test('the actual read-only page probe rejects login or missing list content', () => {
  const code = read('patterns/page-probes.md').match(/<<'JS'\n([\s\S]*?)\nJS/)[1];
  const document = { querySelector: () => null, querySelectorAll: () => [] };
  const location = { href: 'https://example.invalid/auth_login/', pathname: '/auth_login/' };
  const context = vm.createContext({ document, location });
  assert.equal(vm.runInContext(code, context).ok, false);
  location.pathname = '/eec/instances';
  assert.equal(vm.runInContext(code, context).ok, false);
  document.querySelector = () => ({ innerText: 'table' });
  assert.equal(vm.runInContext(code, context).ok, true);
});
