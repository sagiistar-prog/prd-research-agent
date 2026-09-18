"""Compare validated local PRD snapshots. No model, network, or approval inference."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def checked_snapshot(payload):
    from jsonschema import Draft202012Validator
    from plugin_run import run
    Draft202012Validator(json.loads((ROOT/'schemas/output.schema.json').read_text(encoding='utf-8'))).validate(payload)
    if payload['status'] != 'ok' or payload['result']['product_plan'] is None:
        raise ValueError('Compare two result.json files with authored product plans.')
    result = payload['result']; analysis = result['analysis']
    verified = run({'requirement_markdown': analysis['requirement_markdown'],
                    'competitors': analysis['competitors'], 'product_plan': result['product_plan']})['result']
    if verified['analysis'] != analysis:
        raise ValueError('Snapshot evidence was changed. Regenerate result.json from the original inputs.')
    # Recompute checks and ignore cached summaries, Markdown and backlog.
    return {'analysis': verified['analysis'], 'plan': verified['product_plan']}


def compare(before, after, allow_product_rename=False):
    old, new = checked_snapshot(before), checked_snapshot(after)
    a, b = old['plan'], new['plan']
    if a['product_name'] != b['product_name'] and not allow_product_rename:
        raise ValueError('Product names differ. Use --allow-product-rename only for revisions of the same product.')
    left = {f['id']: f for f in a['features']}; right = {f['id']: f for f in b['features']}
    changes = []
    for identifier in sorted(left.keys() | right.keys()):
        previous, current = left.get(identifier), right.get(identifier)
        if previous == current: continue
        fields = sorted(k for k in (previous or {}).keys() | (current or {}).keys()
                        if (previous or {}).get(k) != (current or {}).get(k))
        changes.append({'id': identifier, 'kind': 'added' if previous is None else 'removed' if current is None else 'modified',
                        'name': (current or previous)['name'], 'fields': fields,
                        'before': previous, 'after': current})
    sections = [{'field': k, 'before': a.get(k), 'after': b.get(k)} for k in sorted(a.keys() | b.keys())
                if k not in {'features', 'analysis_id', 'schema_version'} and a.get(k) != b.get(k)]
    before_order, after_order = list(left), list(right)
    inputs_changed = old['analysis']['analysis_id'] != new['analysis']['analysis_id']
    reasons = {identifier: set() for identifier in right}
    for change in changes:
        if change['id'] in right: reasons[change['id']].add('功能本身发生变化')
        # Traverse both validated graphs, including dependencies removed in the revision.
        frontier = {change['id']}; visited = set(frontier)
        while frontier:
            following = {f['id'] for f in [*left.values(), *right.values()]
                         if set(f['dependencies']) & frontier} - visited
            for identifier in following & right.keys(): reasons[identifier].add('依赖功能变化：'+change['id'])
            visited |= following; frontier = following
    if inputs_changed or sections:
        for value in reasons.values(): value.add('输入依据变化，需重新核对' if inputs_changed else '规划背景变化，需重新核对')
    report = {'schema_version': '1.0', 'kind': 'prd-revision-comparison',
              'before_snapshot': sha256(canonical(old).encode()).hexdigest(),
              'after_snapshot': sha256(canonical(new).encode()).hexdigest(),
              'product_name': b['product_name'], 'inputs_changed': inputs_changed,
              'feature_order_changed': before_order != after_order,
              'before_order': before_order, 'after_order': after_order,
              'summary': {kind: sum(c['kind'] == kind for c in changes) for kind in ('added', 'removed', 'modified')},
              'features': changes, 'sections': sections,
              'input_changes': [{'field': k, 'before': old['analysis'][k], 'after': new['analysis'][k]}
                                for k in ('requirement_markdown', 'competitors') if old['analysis'][k] != new['analysis'][k]],
              'review_candidates': [{'id': key, 'name': right[key]['name'], 'reasons': sorted(value)}
                                    for key, value in sorted(reasons.items()) if value],
              'approval_status': 'not_approved', 'comparison_scope': 'structural_changes_and_conservative_review_candidates'}
    from jsonschema import Draft202012Validator
    Draft202012Validator(json.loads((ROOT/'schemas/comparison.schema.json').read_text(encoding='utf-8'))).validate(report)
    return report


LABELS = {'name':'名称', 'scope':'版本范围', 'priority':'优先级', 'priority_rationale':'取舍理由',
          'dependencies':'前置功能', 'stories':'用户故事与验收条件', 'subfeatures':'子功能', 'problem_ids':'关联问题',
          'basis':'依据与假设', 'objective':'产品目标', 'users':'目标用户', 'problems':'用户问题',
          'constraint_responses':'约束响应', 'assumptions':'待验证假设', 'metrics':'指标', 'out_of_scope':'排除项',
          'open_questions':'待澄清问题', 'rollout':'发布次序', 'product_name':'产品名称',
          'requirement_markdown':'需求原文', 'competitors':'竞品资料'}


def render_markdown(report):
    import html
    import re
    def literal(text):
        return re.sub(r'([\\`*_{}\[\]()#+.!|>-])', r'\\\1', html.escape(text).replace('\n', ' ').replace('\r', ' '))
    lines = ['# 需求版本比较', '', literal(report['product_name']), '', '这是变更清单与重新评审提示，不是批准记录。', '',
             f"旧快照：{report['before_snapshot']}", f"新快照：{report['after_snapshot']}", '']
    for change in report['features']:
        lines += [f"## {literal(change['id'])} / {literal(change['name'])}", change['kind'], '']
        for field in change['fields']:
            lines += ['### '+LABELS.get(field,field), '', '变更前', '']
            lines += ['    '+s for s in json.dumps((change['before'] or {}).get(field), ensure_ascii=False, indent=2).splitlines()]
            lines += ['', '变更后', '']
            lines += ['    '+s for s in json.dumps((change['after'] or {}).get(field), ensure_ascii=False, indent=2).splitlines()]
    for change in [*report['sections'], *report['input_changes']]:
        lines += ['', '## '+LABELS.get(change['field'],change['field']), '', '变更前', '']
        lines += ['    '+s for s in json.dumps(change['before'],ensure_ascii=False,indent=2).splitlines()]
        lines += ['', '变更后', '']
        lines += ['    '+s for s in json.dumps(change['after'],ensure_ascii=False,indent=2).splitlines()]
    if report['feature_order_changed']: lines += ['', '## 功能显示次序', '旧：'+', '.join(report['before_order']), '新：'+', '.join(report['after_order'])]
    lines += ['', '## 建议重新评审', '']
    lines += [f"- {literal(row['id'])} {literal(row['name'])}：{literal('；'.join(row['reasons']))}" for row in report['review_candidates']]
    if not report['features'] and not report['sections'] and not report['inputs_changed'] and not report['feature_order_changed']:
        lines += ['没有结构变化；这不表示方案已获批准。']
    return '\n'.join(lines)+'\n'


def render_html(report):
    import html
    import re
    assets = ROOT/'assets/review'
    data = json.dumps({'report':report,'markdown':render_markdown(report),'labels':LABELS}, ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    values = {'TITLE':html.escape(report['product_name']), 'STYLE':(assets/'style.css').read_text(encoding='utf-8')+'\n'+(assets/'comparison.css').read_text(encoding='utf-8'),
              'SCRIPT':(assets/'comparison.js').read_text(encoding='utf-8'), 'DATA':data}
    return re.sub(r'__(TITLE|STYLE|SCRIPT|DATA)__',lambda m:values[m[1]],(assets/'comparison.html').read_text(encoding='utf-8'))


def read(path):
    if path.stat().st_size > 8_000_000: raise ValueError('Snapshot exceeds 8 MB.')
    return json.loads(path.read_text(encoding='utf-8-sig'), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON number.')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',type=Path,required=True); parser.add_argument('--after',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True); parser.add_argument('--allow-product-rename',action='store_true')
    args = parser.parse_args()
    try:
        report = compare(read(args.before), read(args.after), args.allow_product_rename)
        destination = args.output_dir.resolve(); allowed=(ROOT/'output').resolve()
        if not destination.is_relative_to(allowed) or destination==allowed: raise ValueError('Choose a new directory inside output/.')
        page=render_html(report); notes=render_markdown(report)
        destination.mkdir(parents=True,exist_ok=False)
        for name,content in [('changes.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n'),('changes.md',notes),('review.html',page)]:
            (destination/name).write_bytes(content.encode('utf-8'))
        print(json.dumps({'status':'ok','summary':report['summary'],'review_candidates':len(report['review_candidates']),'approval_status':'not_approved'}));return 0
    except Exception as error:
        message = str(error) if type(error) is ValueError else 'Check valid snapshots and a fresh output directory; existing files are preserved.'
        print(json.dumps({'status':'error','message':message},ensure_ascii=False));return 2


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');raise SystemExit(main())
