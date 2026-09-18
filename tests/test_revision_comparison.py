import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from plugin_run import run
from compare_revisions import compare, render_html


class RevisionComparisonTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/plugin-input.json').read_text(encoding='utf-8'))
        self.data['product_plan']=json.loads((ROOT/'examples/team-pulse-plan.json').read_text(encoding='utf-8'))
        self.before=run(self.data)

    def test_same_snapshot_has_no_changes_and_no_approval(self):
        result=compare(self.before,self.before)
        self.assertEqual(result['summary'],{'added':0,'removed':0,'modified':0})
        self.assertEqual(result['before_snapshot'],result['after_snapshot'])
        self.assertEqual(result['review_candidates'],[])
        self.assertEqual(result['approval_status'],'not_approved')

    def test_acceptance_edit_marks_transitive_dependents_in_both_graphs(self):
        changed=copy.deepcopy(self.data)
        changed['product_plan']['features'][0]['stories'][0]['acceptance'][0]['then']='虚构修订：先核对匿名阈值，再显示统计。'
        result=compare(self.before,run(changed))
        self.assertEqual(result['summary']['modified'],1)
        self.assertEqual(result['features'][0]['fields'],['stories'])
        self.assertEqual({r['id'] for r in result['review_candidates']},{'F1','F2','F3','F4'})
        self.assertIn('依赖功能变化：F1',next(r for r in result['review_candidates'] if r['id']=='F3')['reasons'])

    def test_removed_dependency_remains_visible_to_review(self):
        changed=copy.deepcopy(self.data);plan=changed['product_plan']
        plan['features'][1]['dependencies']=[]
        result=compare(self.before,run(changed))
        self.assertEqual(result['features'][0]['before']['dependencies'],['F1'])
        self.assertEqual(result['features'][0]['after']['dependencies'],[])
        self.assertEqual({r['id'] for r in result['review_candidates']},{'F2','F3','F4'})

    def test_reorder_does_not_invent_priority_change(self):
        changed=copy.deepcopy(self.data);changed['product_plan']['features'].reverse()
        result=compare(self.before,run(changed))
        self.assertTrue(result['feature_order_changed'])
        self.assertEqual(result['features'],[])

    def test_stale_plan_or_tampered_evidence_rejected(self):
        for mutation in ['text','hash','plan']:
            changed=copy.deepcopy(self.before)
            if mutation=='text':changed['result']['analysis']['evidence'][0]['text']='Forged source'
            elif mutation=='hash':changed['result']['analysis']['analysis_id']='0'*64
            else:changed['result']['product_plan']['analysis_id']='0'*64
            with self.assertRaises(ValueError):compare(self.before,changed)

    def test_cached_checks_are_not_authority(self):
        changed=copy.deepcopy(self.before)
        changed['result']['markdown']='Untrusted cached text'
        result=compare(self.before,changed)
        self.assertEqual(result['before_snapshot'],result['after_snapshot'])

    def test_context_change_and_explicit_product_rename(self):
        changed=copy.deepcopy(self.data);changed['product_plan']['product_name']='Renamed fictional product'
        after=run(changed)
        with self.assertRaisesRegex(ValueError,'Product names differ'):compare(self.before,after)
        result=compare(self.before,after,True)
        self.assertEqual(len(result['review_candidates']),4)
        self.assertEqual(result['sections'][0]['field'],'product_name')

    def test_changed_input_rechecks_all_and_not_just_feature_text(self):
        from requirements_analysis import assess
        changed=copy.deepcopy(self.data);changed['requirement_markdown']+='\n补充背景：此处是新的虚构评审记录。'
        changed['product_plan']['analysis_id']=assess(changed['requirement_markdown'],changed.get('competitors',[]))['analysis_id']
        result=compare(self.before,run(changed))
        self.assertTrue(result['inputs_changed']);self.assertEqual(result['features'],[])
        self.assertEqual(len(result['review_candidates']),4)
        self.assertEqual(result['input_changes'][0]['after'],changed['requirement_markdown'])

    def test_new_ids_are_add_remove_not_guessed_renames(self):
        changed=copy.deepcopy(self.data);plan=changed['product_plan']
        plan['features'][-1]['id']='F5'
        for stage in plan['rollout']:stage['feature_ids']=['F5' if id=='F4' else id for id in stage['feature_ids']]
        for response in plan['constraint_responses']:
            response['feature_ids']=['F5' if id=='F4' else id for id in response['feature_ids']]
        result=compare(self.before,run(changed))
        self.assertEqual(result['summary'],{'added':1,'removed':1,'modified':0})

    def test_html_cannot_close_data_script(self):
        changed=copy.deepcopy(self.data);changed['product_plan']['features'][0]['name']='</script><script>window.pwned=true</script>'
        html=render_html(compare(self.before,run(changed)))
        self.assertNotIn('</script><script>window.pwned',html)

    def test_cli_preserves_existing_output_and_returns_structured_error(self):
        (ROOT/'output').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as directory:
            path=Path(directory);source=path/'result.json';source.write_text(json.dumps(self.before),encoding='utf-8')
            args=[sys.executable,str(ROOT/'scripts/compare_revisions.py'),'--before',str(source),'--after',str(source),'--output-dir',str(path/'comparison')]
            first=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stdout+first.stderr)
            files={p.name:p.read_bytes() for p in (path/'comparison').iterdir()}
            second=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(second.returncode,2)
            self.assertEqual(json.loads(second.stdout)['status'],'error')
            self.assertEqual(files,{p.name:p.read_bytes() for p in (path/'comparison').iterdir()})


if __name__=='__main__':unittest.main()
