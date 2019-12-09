import click
from fetcher import Fetcher
import logging

@click.command()
@click.option('--agfid', default="", type=str, help='agfid, default=Create new agfid')

@click.option('--u_ip', default="39.108.80.53", type=str,  help='upload node ip, default=39.108.80.53')
@click.option('--d_ip', default="39.108.80.53", type=str,  help='download node ip, default=39.108.80.53')
@click.option('--r_ip', default="39.108.80.53", type=str,  help='retrievel node ip, default=39.108.80.53')
@click.option('--a_ip', default="39.108.80.53", type=str,  help='adc node ip, default=39.108.80.53')

@click.option('--u_port', default="8074", type=int, help='upload node port, default=8074')
@click.option('--d_port', default="8072", type=int, help='download node port, default=8072')
@click.option('--r_port', default="8074", type=int, help='retrievel node port, default=8073')
@click.option('--a_port', default="8002", type=int, help='adc node port, default=8002')

@click.option('--temp_file_dir', default="./", type=str, help='temp file dir, default=./')
@click.option('--device_name', default="video0", type=str, help='video device name, default=video0')

def fetch(agfid, u_ip, d_ip, r_ip, a_ip, u_port, d_port, r_port, a_port, temp_file_dir, device_name):
    
    logging.basicConfig(filename="fetcher.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
    logging.info('_r=true' + ';agfid=' + agfid + ';a_port=' + str(a_port) + ';u_port=' + str(u_port) + ';r_port=' + str(r_port) + ';temp_file_dir=' + temp_file_dir + ';device_name=' + device_name + ';')
    
    params = {
        "rnode_ip" : r_ip,
        "unode_ip" : u_ip,
        "dnode_ip" : d_ip,
        "unode_port" : str(u_port),
        "rnode_port" : str(r_port),
        "dnode_port" : str(d_port),
        "adc_ip" : a_ip,
        "adc_port" : str(a_port)
    }
    
    fetcher = Fetcher(params)
    err = fetcher.start(agfid=agfid, device_name=device_name, temp_file_dir=temp_file_dir)
    if err is not None:
        click.echo("_r=false;message="+err+";")
        logging.error("_r=false;message="+err+";")
        
    if fetcher.ffmpeg != None:
        fetcher.ffmpeg.kill()

@click.group()
def cli():
    pass

if __name__ == '__main__':
   cli.add_command(fetch)
   cli()