import os
import datetime
import glob
import db
import dblite
import sys
import time
import subprocess
from log import Log
from dotenv import load_dotenv

load_dotenv()

app_dir = os.getenv('APP_DIR')
storage_dir = app_dir + '/storage/app/passes'

pass_ = {
'site_id':60,
'detection_id':6297635,
'measured_at':'2024-09-01 00:42:07',
'plate':'OFQ9A17'
}

print(pass_)

query = f'''
	SELECT
		p.id,
		p.measured_at,
		p.image_zoom,
		p.image_amb1,
		p.image_amb2,
  		(
			p.assessment_date IS NOT NULL
			OR EXISTS (SELECT pi.id FROM pass_irregularities as pi WHERE pi.pass_id = p.id LIMIT 1)
		) as has_irregularity
	FROM passes as p
	WHERE
		p.site_id = {pass_['site_id']}
		AND p.detection_id = {pass_['detection_id']}
		AND p.measured_at = '{pass_['measured_at']}'
		AND p.plate = '{pass_['plate']}'
	LIMIT 1
    '''

pass_db = db.find(query)
pass_id = pass_db['id'] if pass_db else None

#elapsed = round(time.time() - t0, 2)
#Log.debug(f'[PROCESS] Busca pela passagem: {pass_}: {elapsed}s')

remove_files = not pass_db or (not pass_db['has_irregularity'] and (datetime.datetime.now() - pass_db['measured_at']).days >= 3)

print(pass_db, remove_files)
