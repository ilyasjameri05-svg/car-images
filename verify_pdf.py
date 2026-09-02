import re, os
path = 'sample_sudoku_book.pdf'
size = os.path.getsize(path)
print(f'File size: {size:,} bytes')
with open(path, 'rb') as f:
    content = f.read()
matches = re.findall(rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]', content)
pts_per_in = 72.0
print(f'Pages with MediaBox: {len(matches)}')
for i, m in enumerate(matches[:3]):
    w = float(m[2]) - float(m[0])
    h = float(m[3]) - float(m[1])
    print(f'  Page {i+1}: {w:.1f} x {h:.1f} pt  ({w/pts_per_in:.3f}" x {h/pts_per_in:.3f}")')
if matches:
    m = matches[0]
    w = float(m[2]) - float(m[0])
    h = float(m[3]) - float(m[1])
    print(f'Dimensions match 6x9: {abs(w-432)<1 and abs(h-648)<1}')
print('PDF header OK:', content[:4] == b'%PDF')
