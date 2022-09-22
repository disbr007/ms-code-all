from osgeo import gdal

co = ["COMPRESS=LZW"]
gdal.Translate(creationOptions=co)
