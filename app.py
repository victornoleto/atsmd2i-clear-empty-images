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

def remove_file(file, pass_id = None):

	# get file size in kb
	size = os.path.getsize(file) / 1024
	size = round(size, 2)

	try:

		os.remove(file)

		row = {
			'path': file,
			'kb': size,
			'pass_id': pass_id
		}

		dblite.insert('history', row)

		Log.info(f'[REMOVE] Arquivo removido com sucesso: {file}')

	except Exception as e:
		Log.error(f'[REMOVE] Não foi possível remover o arquivo: {file}: {e}')

def process_pass(pass_):

	t0 = time.time()

	# convert measured_at to date object
	date_obj = datetime.datetime.strptime(pass_['measured_at'], '%Y-%m-%d %H:%M:%S')
	
	# remove 5 seconds
	min_date = date_obj - datetime.timedelta(seconds=5)
	max_date = date_obj + datetime.timedelta(seconds=5)

	min_date_format = min_date.strftime('%Y-%m-%d %H:%M:%S')
	max_date_format = max_date.strftime('%Y-%m-%d %H:%M:%S')

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
		AND p.plate = '{pass_['plate']}'
		AND p.measured_at >= '{min_date_format}'
		AND p.measured_at <= '{max_date_format}'
	LIMIT 1
    '''
	#AND p.measured_at = '{pass_['measured_at']}'

	pass_db = db.find(query)
	pass_id = pass_db['id'] if pass_db else None

	if pass_db:
		pass_['id'] = pass_id
		pass_['has_irregularity'] = pass_db['has_irregularity']

	elapsed = round(time.time() - t0, 2)
	Log.debug(f'[PROCESS] Busca pela passagem: {pass_}: {elapsed}s')

	remove_files = not pass_db or (not pass_db['has_irregularity'] and (datetime.datetime.now() - pass_db['measured_at']).days >= 3)
	
	if remove_files:

		if 'image_zoom' in pass_ and pass_['image_zoom']:
			remove_file(pass_['image_zoom'], pass_id)
		
		if 'image_amb1' in pass_ and pass_['image_amb1']:
			remove_file(pass_['image_amb1'], pass_id)

		if 'image_amb2' in pass_ and pass_['image_amb2']:
			remove_file(pass_['image_amb2'], pass_id)

def remove_empty(path):
	Log.debug('Removendo pastas vazias: ' + path)
	subprocess.run(['find', path, '-empty', '-type', 'd', '-delete'])

def process(folder):

	path = storage_dir + '/' + folder

	if not os.path.exists(path):
		raise Exception('Pasta não encontrada: ' + path)

	folder_parts = folder.split('/')

	if len(folder_parts) < 4:

		folder_children = os.listdir(path)
		folder_children.sort()

		for folder_child in folder_children:
			process(folder + '/' + folder_child)

		remove_empty(path)
		return

	t0 = time.time()

	Log.debug('Iniciando processamento da pasta: ' + path)

	# get all files recursively
	files = glob.glob(path + '/**/*', recursive=True)

	# filter only files
	files = [file for file in files if os.path.isfile(file)]

	elapsed = round(time.time() - t0, 2)

	Log.debug(f'Processando pasta: {path}, {len(files)} arquivos - {elapsed}s')

	if len(files) > 0:
	
		passes = {}

		for file in files:

			filename = file.split('/')[-1]
			parts = filename.split('-')

			if len(parts) == 6 and len(parts[0]) == 13:
				# remove the first part
				parts = parts[1:]

			if 'thumb' in file:
				remove_file(file)
				continue

			if not 'zoom' in filename and not 'amb1' in filename and not 'amb2' in filename:
				remove_file(file)
				continue

			if len(parts) < 4:
				remove_file(file)
				continue

			measured_at = parts[3]

			# convert YmdHis to Y-m-d H:i:s
			if measured_at and len(measured_at) == 14:
				measured_at = measured_at[:4] + '-' + measured_at[4:6] + '-' + measured_at[6:8] + ' ' + measured_at[8:10] + ':' + measured_at[10:12] + ':' + measured_at[12:14]
			else:
				measured_at = None
			
			pass_data = {
				'site_id': parts[0],
				'detection_id': parts[1],
				'plate': parts[2],
				'measured_at': measured_at,
			}

			if not pass_data['site_id'] or not pass_data['detection_id'] or not pass_data['plate'] or not pass_data['measured_at']:
				remove_file(file)
				continue

			pass_id = pass_data['site_id'] + '-' + pass_data['detection_id'] + '-' + pass_data['plate']

			if not pass_id in passes:
				passes[pass_id] = pass_data

			if 'zoom' in filename:
				passes[pass_id]['image_zoom'] = file

			if 'amb1' in filename:
				passes[pass_id]['image_amb1'] = file

			if 'amb2' in filename:
				passes[pass_id]['image_amb2'] = file

		passes = list(passes.values())

		#for pass_ in passes:
		for index, pass_ in enumerate(passes):
			try:
				t0 = time.time()
				process_pass(pass_)
				elapsed = round(time.time() - t0, 2)
				Log.debug(f'[PROCESS] Processado {folder} {index + 1}/{len(passes)} - {elapsed}s')
			except Exception as e:
				Log.error(f'[PROCESS] Erro ao processar passagem ({pass_}): {e}')

	# remover pastas vazias
	remove_empty(path)

dblite.init()

args = sys.argv

if len(args) > 1:
	process(args[1])
else:
	print('Informe o nome da pasta a ser processada.')
