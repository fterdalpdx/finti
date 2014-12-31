from setuptools import setup
import os
from distutils.command.install import install

class FintiInstall(install):
	def run(self):
		install.run(self)
		
		self.nginx_conf()
		
	def nginx_conf(self):
		setup_dir = os.path.dirname(os.path.realpath(__file__))
		nginx_template = open(setup_dir + '/src/main/resources/nginx.conf')
		nginx_conf = open(setup_dir + '/nginx/conf/nginx.conf', 'w')
		print('filtering: src: ' + setup_dir + '/src/main/resources/nginx.conf' + ', to: ' + setup_dir + '/nginx/conf/nginx.conf')
		for line in nginx_template:
			nginx_conf.write(line.replace('$BASE', setup_dir))
		nginx_conf.close()
		nginx_template.close()


setup(
    name="finti",
    version="1.0",
    install_requires= [
        "Beaver",
        "ipython",
    ],
	cmdclass = {'install': FintiInstall},
)

