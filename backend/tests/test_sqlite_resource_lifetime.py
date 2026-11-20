import os,subprocess,sys,textwrap,sqlite3
import pytest
from app.sqlite_resources import ClosingConnection

def test_transaction_commits_rolls_back_and_closes(tmp_path):
 path=tmp_path/'transactions.db'
 with sqlite3.connect(path,factory=ClosingConnection) as db:
  db.execute('CREATE TABLE values_test(value INTEGER)');db.execute('INSERT INTO values_test VALUES (1)')
 with pytest.raises(sqlite3.ProgrammingError):db.execute('SELECT 1')
 with pytest.raises(RuntimeError):
  with sqlite3.connect(path,factory=ClosingConnection) as db:
   db.execute('INSERT INTO values_test VALUES (2)');raise RuntimeError('rollback')
 with sqlite3.connect(path,factory=ClosingConnection) as read:
  assert read.execute('SELECT value FROM values_test').fetchall()==[(1,)]

def test_queue_polling_survives_low_descriptor_limit_without_gc(tmp_path):
 if sys.platform=='win32':pytest.skip('POSIX descriptor limit regression')
 code=textwrap.dedent('''
 import gc,resource,sys
 from app.jobs import PersistentJobQueue
 soft,hard=resource.getrlimit(resource.RLIMIT_NOFILE)
 resource.setrlimit(resource.RLIMIT_NOFILE,(min(128,hard),hard))
 gc.disable()
 queue=PersistentJobQueue(sys.argv[1])
 for _ in range(300):queue.queue_status()
 print('300 queue polls passed with GC disabled and a 128-descriptor limit')
 ''')
 result=subprocess.run([sys.executable,'-c',code,str(tmp_path/'queue.sqlite3')],capture_output=True,text=True,timeout=60)
 assert result.returncode==0,result.stderr
