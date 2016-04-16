# datasheetCollection
read BOM manufacturer part #s, retrieve datasheet for corresponding parts

usage:

python datasheetCollect.py datasheets.csv "Vendor Part Number" Files

Where:
  datasheets.csv : contains manufactuer/vendor part numbers (MPNs)
  "Vendor Part Number" : the column header containing the MPNs
  Files : Directory located where program is launched from to where .pdfs are to be stored
