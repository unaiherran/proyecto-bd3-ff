export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

nohup /home/ec2-user/.local/bin/pipenv run python3 merge_csv_files.py 2> /home/ec2-user/proyecto-bd3-ff/DatosTraficoTiemporeal/merge_error &
