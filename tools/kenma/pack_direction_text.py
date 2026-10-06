"""Encode the exact Kenma08 direction words as byte-plane base64 C++ text."""
from pathlib import Path
import base64,hashlib,json,re,shutil,struct,zipfile
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
src=ROOT/'bots/kenma-08-lossless-direction'
dst=ROOT/'bots/kenma-16-lossless-model-text'
assert not dst.exists(), 'Never overwrite a measured snapshot'
s=(src/'hb1_direction_compact.hpp').read_text()
prefix,body=s.split('inline constexpr unsigned int dirc_nodes[] = {',1)
words=[int(x,16) for x in re.findall(r'0x[0-9a-fA-F]+',body)]
raw=struct.pack('<'+'I'*len(words),*words)
plane_bytes=(len(words)+2)//3*3
planes=b''.join(raw[k::4]+bytes(plane_bytes-len(words)) for k in range(4))
text=base64.b64encode(planes).decode('ascii')
decoded=base64.b64decode(text)
restored=[sum(decoded[k*plane_bytes+i]<<(8*k) for k in range(4)) for i in range(len(words))]
assert restored==words
shutil.copytree(src,dst)
new=prefix+f'inline constexpr int dirc_node_count = {len(words)};\ninline constexpr int dirc_plane_chars = {plane_bytes//3*4};\ninline constexpr char dirc_node_text[] =\n'
new+=''.join('"'+text[i:i+120]+'"\n' for i in range(0,len(text),120))+';\n'
lookup=[0]*128
for i,c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'):lookup[ord(c)]=i
new+='inline constexpr unsigned char dirc_b64[] = {'+','.join(map(str,lookup))+'};\n'
new+=r"""
inline unsigned int dirc_pair(int pos) {
    return (static_cast<unsigned int>(dirc_b64[static_cast<unsigned char>(dirc_node_text[pos])])<<6)
        | dirc_b64[static_cast<unsigned char>(dirc_node_text[pos+1])];
}
inline unsigned int dirc_node(int index) {
    int k=index%3, pos=(index/3)*4+k, shift=4-2*k;
    return ((dirc_pair(pos)>>shift)&255u)
        | (((dirc_pair(pos+dirc_plane_chars)>>shift)&255u)<<8)
        | (((dirc_pair(pos+2*dirc_plane_chars)>>shift)&255u)<<16)
        | (((dirc_pair(pos+3*dirc_plane_chars)>>shift)&255u)<<24);
}
} // namespace hb1
"""
(dst/'hb1_direction_compact.hpp').write_text(new)
p=dst/'hb1_compact.hpp'
s=p.read_text().replace('unsigned int const* nd = dirc_nodes + dirc_tree_start[t];','int root = dirc_tree_start[t];').replace('unsigned int w = nd[j];','unsigned int w = dirc_node(root+j);')
p.write_text(s)
(dst/'README.md').write_text("""# Kenma16 — lossless model source text

Parent: kenma-08-lossless-direction, strategy equivalent to03. Store the same32-bit node words as four byte planes in base64 C++ string literals. Decode only each visited word during inference; no whole-model startup decoding, model retraining, quantization or policy change. All thresholds and leaf bits remain exact. The source generator reconstructs every word.

Purpose: recover archive space for the combined encoder/HB direction prior while preserving the existing model needed to provide its HB probability inputs. This is a storage control, not a strength claim. Native node/probability parity and exact-source sandbox turn-cost checks are required before adoption. No reserved seeds or new maps.

Status: generated, unmeasured. Reproduce with tools/kenma/pack_direction_text.py.
""")
out=MAIN/'build/kenma/lossless-model-text';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/f'{dst.name}.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dst.iterdir()):
        if p.is_file():z.write(p,p.name)
report={'parent':src.name,'bot':dst.name,'nodes':len(words),'node_words_reconstructed':len(words),'encoded_chars':len(text),'zip_bytes':(out/f'{dst.name}.zip').stat().st_size,'parent_header_sha256':hashlib.sha256((src/'hb1_direction_compact.hpp').read_bytes()).hexdigest()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
