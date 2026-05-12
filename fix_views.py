f=open('pages/views.py',encoding='utf-8').read() 
f=f.replace('NOW()','CURRENT_TIMESTAMP') 
open('pages/views.py','w',encoding='utf-8').write(f) 
print('done') 
