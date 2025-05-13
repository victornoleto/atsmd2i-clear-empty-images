filename = '68029f7e2eed0-99-1459514-KPH5185-20250418154848-zoom.jpg'

parts = filename.split('-')

if len(parts) == 6 and len(parts[0]) == 13:
	# remove the first part
	parts = parts[1:]

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

print(len(parts), pass_data)