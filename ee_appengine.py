#!/usr/bin/env python
"""A simple example of connecting to Earth Engine using App Engine."""



# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.

import os
import json
import config
import sys

def fix_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

fix_path()
import ee
import jinja2
import webapp2
from google.appengine.api import memcache

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

EE_CREDENTIALS = ee.ServiceAccountCredentials(config.EE_ACCOUNT, config.EE_PRIVATE_KEY_FILE)
class MainPage(webapp2.RequestHandler):
  def get(self):                             # pylint: disable=g-bad-name
    """Request an image from Earth Engine and render it to a web page."""
    
    ee.Initialize(EE_CREDENTIALS)
    region = ee.Geometry.Polygon([[-64.51171875, -5.090944175033373], [-58.359375, -7.18810087117902],[-58.18359375, -2.1088986592431254]]);

    def area_analisis(region):
        IMAGE_COLLECTION_ID = 'GME/layers/12520323906563193292-05039038523903420493'
        image =ee.ImageCollection(IMAGE_COLLECTION_ID).mosaic()
        #image = images.mosaic()
        #mapid = image.getMapId({'min': 0, 'max': 1000})
        reduce_args = {
            'reducer': ee.Reducer.sum(),
            'geometry': region,
            'bestEffort': True,
            'scale': 3000,
            'maxPixels': 10000000,
            'tileScale': 1
            }
        multi = (10000*255)
        area_stats = image.float().divide(multi).multiply(ee.Image.pixelArea()).reduceRegion(**reduce_args)
        return area_stats.getInfo()
        #return images
    # These could be put directly into template.render, but it
    # helps make the script more readable to pull them out here, especially
    # if this is expanded to include more variables.
    template_values = {
        'area': area_analisis(region)['b1']
    }
    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
