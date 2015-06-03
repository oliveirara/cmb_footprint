import ConfigParser
import urllib2
import os
import hashlib

import healpy as H
import numpy as np

import util

class ConfigHandler(object):
    def __init__(self, config_fn, map_path, nside=256, download_config=False):
        self.nside = nside
        self.config_fn = config_fn
        self.map_path = map_path

        if download_config:
            self.get_config()

        self.config = ConfigParser.ConfigParser()
        self.config.read(config_fn)
        self.check_all()

    def get_config(self):
        '''Download the configuration file from LAMBDA to the filename given
        in self.config_fn in the local directory.
        
        Notes
        -----
        Remote file is footprint.txt instead of footprint.cfg because server
        gives an error if you try to download a .cfg file whereas it allows
        you to download a .txt file.
        '''

        url_pre = 'http://lambda.gsfc.nasa.gov/data/footprint-maps/'
        
        local_path = os.path.join('./', self.config_fn)
        url = os.path.join(url_pre, 'footprint.txt')

        print("Downloading configuration file")

        file_chunk = 16 * 1024
        req = urllib2.urlopen(url)
        with open(local_path, 'wb') as fp1:
            while True:
                chunk = req.read(file_chunk)
                if not chunk:
                    break
                fp1.write(chunk)
    

    def check_all(self):
        '''Check if we have all the correct hitmaps downloaded locally
        for experiments in which we provide Healpix files'''
        
        for section in self.config.sections():
            handler = self.config.get(section,'handler')
            if handler == 'hpx_file':
                junk = self.download_files(section)
        
    def load_experiment(self, experiment_name):

        try:
            handler = self.config.get(experiment_name,'handler')
        except:
            raise ValueError("We do not have information for this experiment")

        if handler == 'hpx_file':
            hpx_map = self.get_hpx_file(experiment_name)
        elif handler == 'radec_range':
            hpx_map = self.get_radec_range(experiment_name)
        elif handler == 'radec_disc':
            hpx_map = self.get_radec_disc(experiment_name)
        elif handler == 'radec_polygon':
            hpx_map = self.get_radec_polygon(experiment_name)
        elif handler == 'combination':
            hpx_map = self.get_combination(experiment_name)

        return hpx_map

    def download_files(self, experiment_name):
        '''Return the local paths to the files associated with an experiment.
        If the files do not exists or their MD5 checksums do not match what is
        stored in the configuration file, download new files.

        Parameters
        ----------
        experiment_name : string
            The experiment for which we want the filenames of the hitmaps

        '''
           
        fns = self.config.get(experiment_name,'file')
        cksums = self.config.get(experiment_name,'checksum')

        fns = fns.split(',')
        cksums = cksums.split(',')

        fns_out = []
#       Compare the checksum of the local file to the value in the
#       configuration file. If they don't match (or local file does not
#       exist), download the file. If the checksum of the downloaded file does
#       not match the checksum in the configuration file something is wrong
        for fn_tmp,cksum_cfg in zip(fns,cksums):
            download_file = False
            local_path = os.path.join(self.map_path, fn_tmp)
            if os.path.exists(local_path):
                cksum_file = hashlib.md5(open(local_path, 'rb').read()).hexdigest()
                if cksum_cfg != cksum_file:
                    download_file = True
            else:
                download_file = True

            if download_file:
                url_pre = 'http://lambda.gsfc.nasa.gov/data/footprint-maps'
                url = os.path.join(url_pre, fn_tmp)
                print("Downloading map for", experiment_name)
                req = urllib2.urlopen(url)
                file_chunk = 16 * 1024
                with open(local_path, 'wb') as fp1:
                    while True:
                        chunk = req.read(file_chunk)
                        if not chunk:
                            break
                        fp1.write(chunk)
                
                cksum_file = hashlib.md5(open(local_path, 'rb').read()).hexdigest()
                if cksum_cfg != cksum_file:
                    print("Remote file checksum does not match cfg checksum")

            fns_out.append(local_path)

        return fns_out

    def get_hpx_file(self, experiment_name):
        
        fns = self.download_files(experiment_name)

        hpx_map = H.read_map(fns[0])
        nside = H.npix2nside(len(hpx_map))
        for fn_tmp in fns[1:]:
            tmp_map = H.read_map(fn_tmp)
            hpx_map += H.ud_grade(tmp_map, nside)

        return hpx_map

    def get_radec_polygon(self, experiment_name):

        ras = []
        decs = []

        i = 1
        while 1:
            radec_point = 'vertex'+str(i)
            print "AAA: ", radec_point
            try:
                radec_val = self.config.get(experiment_name, radec_point)
                radec_val = radec_val.split(',')
                ras.append(float(radec_val[0]))
                decs.append(float(radec_val[1]))
            except:
                break
            i += 1
  
        print ras
        print decs
        vtxs = np.transpose([ras,decs])

        hpx_map = util.gen_hpx_map_bound_polygon(vtxs, self.nside)

        return hpx_map

    def get_radec_disc(self, experiment_name):

        radec_cen = self.config.get(experiment_name, 'radec_cen')
        radec_cen = radec_cen.split(',')
        radec_cen = (float(radec_cen[0]),float(radec_cen[1]))

        radius = float(self.config.get(experiment_name, 'radius'))

        hpx_map = util.gen_hpx_map_bound_disc(radec_cen, radius, self.nside)

        return hpx_map

    def get_combination(self, experiment_name):

        sub_names = self.config.get(experiment_name, 'sub_experiments')

        sub_names = sub_names.split(',')

        hpx_map = self.load_experiment(sub_names[0])
        for sub_name in sub_names[1:]:
            hpx_map += self.load_experiment(sub_name)

        return hpx_map
