import html, sys
from playwright.sync_api import sync_playwright

def term(raw):
    # show what a terminal shows at the end: Spark's [Stage ...] progress bar is
    # drawn with \r and then erased, so only text written after it stays visible
    out = []
    for line in raw.split('\n'):
        if '\r' in line:
            segs = [x for x in line.split('\r') if x.strip() and not x.lstrip().startswith('[Stage')]
            if not segs: continue
            line = segs[-1].strip()
        out.append(line.rstrip())
    return out

def colorize(l):
    e = html.escape(l)
    for p in ['(.venv) root@vm:~/spark_hw1$', 'root@vm:~/spark_hw1$']:
        if l.startswith(p):
            venv = p.startswith('(.venv)')
            pre = '(.venv) ' if venv else ''
            rest = html.escape(l[len(p):])
            return f'{pre}<span class="u">root@vm</span>:<span class="d">~/spark_hw1</span>$' + rest
    if ' WARN ' in l or l.startswith('WARNING'): return f'<span class="w">{e}</span>'
    return e

CSS = '''
body{margin:0;background:#fff;padding:0}
.win{width:%dpx;border-radius:10px 10px 0 0;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.35);border:1px solid #1a1a1a;margin:8px}
.bar{background:#2c2c2c;color:#ddd;font:bold 13px "DejaVu Sans",sans-serif;height:34px;display:flex;align-items:center;justify-content:center;position:relative}
.btns{position:absolute;right:10px;top:9px;display:flex;gap:8px}
.btns span{width:16px;height:16px;border-radius:50%%;background:#454545;display:inline-block}
.btns span.x{background:#e95420}
pre{margin:0;background:#300a24;color:#eeeeec;font:13px/1.35 "Liberation Mono",monospace;padding:8px 10px 10px;white-space:pre-wrap;word-break:break-all}
.u{color:#8ae234;font-weight:bold}.d{color:#729fcf;font-weight:bold}.w{color:#fce94f}
'''
def shot(page, lines, out, width=900, cursor=True):
    body = '\n'.join(colorize(l) for l in lines)
    if cursor: body = body.rstrip() + '<span style="background:#eeeeec"> </span>'
    page.set_content(f'<style>{CSS % width}</style><div class="win"><div class="bar">root@vm: ~/spark_hw1'
                     f'<div class="btns"><span></span><span></span><span class="x"></span></div></div><pre>{body}</pre></div>')
    page.locator('.win').screenshot(path=out)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page(device_scale_factor=2)
    for name in ['s1_install', 's2_warn', 's3_fixed', 's5_parquet']:
        shot(pg, term(open(f'shots/{name}.txt', newline='').read()), f'shots/{name}.png')
    ops = term(open('shots/s4_ops.txt', newline='').read())
    cut = next(i for i, l in enumerate(ops) if l.startswith('=== Op 5'))
    shot(pg, ops[:cut], 'shots/s4_ops_a.png', cursor=False)
    shot(pg, ops[cut:], 'shots/s4_ops_b.png')
    b.close()
