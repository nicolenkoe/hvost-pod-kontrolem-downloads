"""Read back the separately published Hvost release without credentials."""
import pathlib,urllib.request,json,hashlib,time,datetime
ROOT=pathlib.Path(__file__).resolve().parent
BASE='https://nicolenkoe.github.io/hvost-pod-kontrolem-downloads/'
def read(name):
 with urllib.request.urlopen(urllib.request.Request(BASE+name,headers={'Accept-Encoding':'identity'}),timeout=90) as response:
  assert response.status==200;return response.read()
def main():
 release=json.loads((ROOT/'release.json').read_text())
 for attempt in range(20):
  try:
   feed=json.loads(read('update.json?t='+str(time.time_ns())))
   if feed['versionCode']==release['versionCode']:break
  except Exception:pass
  time.sleep(2)
 else:raise RuntimeError('New release not live')
 assert feed['sha256']==release['sha256'] and feed['bytes']==release['bytes']
 data=read(release['fileName']);assert len(data)==release['bytes'] and hashlib.sha256(data).hexdigest()==release['sha256']
 catalog=json.loads(read('versions.json'));assert catalog['latest']==release['versionCode']
 for entry in catalog['releases']:assert entry['downloadUrl']==BASE+entry['fileName']
 for page in ['','testing/','versions/']:
  text=read(page).decode();assert 'Хвост' in text
  assert 'enduro-club-downloads/hvost-pod-kontrolem/' not in text
 for ext in ['mp4','mp3','vtt']:
  name='assets/guide-'+release['version']+'.'+ext;assert read(name)==(ROOT/name).read_bytes()
 voice=json.loads(read('assets/voice-info.json'));assert voice['female'] and voice['version']==release['version']
 report={'version':release['version'],'apkSha256':release['sha256'],'bytes':len(data),'base':BASE,'independentRepository':True,'femaleVoice':voice,'physicalDeviceTested':False,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (ROOT/'public-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS standalone public APK, metadata, links and female guide')
if __name__=='__main__':main()
