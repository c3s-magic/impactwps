export PYWPS_CFG=/home/c4m/impactportal/pywps.cfg
#export PYWPS_PROCESSES=/data/wps/impactportalwpsscripts
export PYWPS_PROCESSES=/data/wps/andrejscombine/impactwps
export PYWPS_TEMPLATES=/data/wps/pywps-3.2.1/pywps/Templates
#export NCARG_ROOT="/home/wps/software/install" 
#export PORTAL_SCRIPTS=/home/wps/pywps/scripts/
export POF_OUTPUT_URL=http://127.0.0.1
export POF_OUTPUT_PATH=/data/wps/wpsoutputs/
#export LD_LIBRARY_PATH=/home/wps/software/install/lib:$LD_LIBRARY_PATH
#export PATH=/home/wps/software/install/bin:$PATH
#export MPLCONFIGDIR=/home/wps/tmp/
#. /home/wps/pywps/wps-virtenv/bin/activate
#export PYTHONPATH=/usr/lib64/python2.6/site-packages/:$PYTHONPATH
. /data/wps/pyvirtenv/bin/activate
export PYTHONPATH=/data/wps/andrejscombine/clipccombine:/data/wps/pywps-3.2.1/build/lib:/data/wps/pyvirtenv/lib/python2.7/site-packages/:/home/c4m/malleefowl:/home/c4m/flyingpigeon:$PYTHONPATH
# export PYTHONPATH=$PYWPS_PROCESSES:$PYTHONPATH
# export PYTHONPATH=/usr/people/mihajlov/python/clipc/clipccombine/:$PYTHONPATH
echo "PythonPath="$PYTHONPATH
python ./test.wps.py

# 
#   <exportenvironment>ADAGUC_CONFIG=/home/c4m/impactportal/adagucserver.xml</exportenvironment>
#     <exportenvironment>ADAGUC_LOGFILE=/data/log/server.log</exportenvironment>
#     <exportenvironment>ADAGUC_ERRORFILE=/data/log/server.errlog</exportenvironment>
#     <exportenvironment>ADAGUC_DATARESTRICTION="SHOW_QUERYINFO|ALLOW_WCS|ALLOW_GFI|ALLOW_METADATA"</exportenvironment>
#     <exportenvironment>PYTHONPATH=/data/wps/andrejscombine/clipccombine/:/data/wps/pywps-3.2.1/build/lib:/data/wps/pyvirtenv/lib/python2.7/site-packages/:/home/c4m/malleefowl:/home/c4m/flyingpigeon</exportenvironment>
#     <exportenvironment>LD_LIBRARY_PATH=/data/software/install/lib:/data/wps/icyclimbackup/indices/:/data/build/lib/:/home/c4m/.conda/envs/birdhouse/lib</exportenvironment>
#     <exportenvironment>PATH=/home/c4m/.conda/envs/birdhouse/bin:/data/software/adagucserver/bin/:/data/wps/pyvirtenv/bin/:/data/build/bin/:/usr/lib/lightdm/lightdm:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games</exportenvironment>
#     <exportenvironment>PYWPS_CFG=/home/c4m/impactportal/pywps.cfg</exportenvironment>
#     <exportenvironment>PYWPS_PROCESSES=/data/wps/impactportalwpsscripts</exportenvironment>
#     <exportenvironment>PYWPS_TEMPLATES=/data/wps/pywps-3.2.1/pywps/Templates</exportenvironment>
#     <exportenvironment>NCARG_ROOT=/data/software/install/</exportenvironment>
#     <exportenvironment>PORTAL_OUTPUT_PATH=/data/wps/wpsoutputs/</exportenvironment>
#     <exportenvironment>PORTAL_OUTPUT_URL=http://localhost/impactportal/WPS?OUTPUT=</exportenvironment>
#     <exportenvironment>PORTAL_SCRIPTS=/data/software/install/htdocs/wpspage/</exportenvironment>
#     <exportenvironment>MPLCONFIGDIR=/home/c4m/matplotlib</exportenvironment>
#     <exportenvironment>USE_FONTCONFIG=False</exportenvironment>
