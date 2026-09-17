import sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from plugin_run import run
class DomainScope(unittest.TestCase):
    def test_non_hr_brief_does_not_invent_hr_features(self):
        data=json.loads((ROOT/'examples/plugin-input.json').read_text(encoding='utf-8'))
        data['requirement_markdown']='# RecipeBox\n帮助家庭整理每周食谱。\n约束：不采集健康数据。'
        data['competitors']=[]
        text=run(data)['result']['markdown']
        self.assertNotIn('People Ops',text)
        self.assertNotIn('匿名反馈',text)
        self.assertIn('不采集健康数据',text)
if __name__=='__main__':unittest.main()
