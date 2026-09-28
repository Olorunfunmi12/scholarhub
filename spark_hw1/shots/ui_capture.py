# Runs the Part 2 operations, keeps the SparkSession open, and screenshots the real Spark Web UI.
import runpy, sys, types
from pyspark.sql import SparkSession
from playwright.sync_api import sync_playwright

real_stop = SparkSession.stop
SparkSession.stop = lambda self: None          # keep the UI alive after the script finishes
runpy.run_path('part2_operations.py', run_name='__main__')
spark = SparkSession.getActiveSession()
url = spark.sparkContext.uiWebUrl
print('UI at', url)

FRAME = '''<style>body{margin:0}.w{width:1280px;border:1px solid #999;border-radius:8px 8px 0 0;overflow:hidden;margin:8px;box-shadow:0 2px 10px rgba(0,0,0,.3)}
.t{background:#dee1e6;height:38px;display:flex;align-items:center;padding:0 12px;gap:10px;font:13px "DejaVu Sans",sans-serif}
.tab{background:#fff;border-radius:8px 8px 0 0;padding:8px 14px;margin-top:6px}
.u{background:#fff;height:36px;display:flex;align-items:center;padding:0 12px;border-bottom:1px solid #ccc;font:13px "DejaVu Sans",sans-serif}
.u span{background:#f1f3f4;border-radius:16px;padding:6px 14px;flex:1;color:#202124}
img{display:block;width:1280px}</style>
<div class="w"><div class="t"><div class="tab">%s</div></div><div class="u"><span>%s</span></div><img src="data:image/png;base64,%s"></div>'''
import base64
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    for path, out in [('/jobs/', 'shots/ui_jobs.png'), ('/SQL/', 'shots/ui_sql.png')]:
        pg.goto(url + path); pg.wait_for_load_state('networkidle')
        title = pg.title()
        raw = base64.b64encode(pg.screenshot()).decode()
        fp = b.new_page(device_scale_factor=1.5)
        fp.set_content(FRAME % (title, 'localhost:4040' + path, raw))
        fp.locator('.w').screenshot(path=out); fp.close()
    b.close()
real_stop(spark)
