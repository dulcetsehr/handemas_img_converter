#!/usr/bin/env python3
#
# converter.py
# Decrypt IDOLM@STER Cinderella Girls KR's encrypted? image files & copy another files
# Support types: png, webp
# 
# Muhotchi (H.K. Kim) dulcetsehr@gmail.com
# Created by 2015-02-21 (Y-M-D) 
#
from __future__ import absolute_import

import os.path
import shutil
import sys

chunks = {
  'png': 0x89,
  'webp': 0x52
}

def get_params():
  args, kargs = [], []
  for v in sys.argv[1:]:
    d = v.strip()
    if d[0] == '-':
      kargs.append(d)
    else:
      args.append(d)
  return (args, kargs)

def process(orig_path, dest_path, target_path, *kargs):
  path1, path2 = os.path.join(orig_path, target_path), os.path.join(dest_path, target_path)
  
  print('Converting on path: %s' % path1)
  # create destination directory if not exists
  if not os.path.exists(path2): os.makedirs(path2)
  
  files = [x for x in os.listdir(path1)]
  
  converted_cnt = 0
  for file in files:
    if os.path.isdir(os.path.join(path1,file)): continue
    ext = os.path.splitext(file)
    if not ext or len(ext) < 2: continue
    filename, ext = ext[0], ext[-1][1:] # remove .(dot)
    if ext not in chunks:
      if '-copy' in kargs:
        shutil.copyfile(os.path.join(path1,file), os.path.join(path2,file))
      continue
    
    with open(os.path.join(path1,file), 'rb') as fp:
      content = fp.read()
      key = chunks[ext] ^ content[0]
      
      # custom key
      for arg in kargs:
        if '-key=' in arg:
          key = int(arg.split('=')[-1], 16)
      
      print('Converting %s as KEY : %02X' % (file, key))
      
      with open(os.path.join(path2,'%s.%s'%(filename,ext)), 'wb') as fp2:
        for i in range(50): # 50 bytes
          fp2.write(bytes([content[i] ^ key]))
        fp2.write(content[50:])
      
      # convert from webp to png
      if ext == 'webp' and '-webp' in kargs:
        try:
          from wand.image import Image
          with Image(filename=os.path.join(path2,'%s.%s'%(filename,ext))) as img:
            with img.convert('png') as converted:
              converted.save(filename=os.path.join(path2,'%s.png'%filename))
          os.remove(os.path.join(path2,'%s.%s'%(filename,ext)))
        except:
          print(' Cannot convert webp to png: catch exception')
      converted_cnt += 1
      print('OK')
  print('%d files converted.' % converted_cnt)
  
  return converted_cnt







def main():
  args, kargs = get_params()
  
  orig_path = args[0] if len(args) > 0 else None
  dest_path = args[1] if len(args) > 1 else None
  if not orig_path or not dest_path:
    print('USAGE: converter.py ORIGINAL_PATH DESTINATION_PATH')
    return
  if not os.path.exists(orig_path):
    print('ERROR : original path not found.')
    return
  if os.path.isfile(orig_path) or os.path.isfile(dest_path):
    print('ERROR : original and destination paths must be directories.')
    return
  
  # create destination directory if not exists
  if not os.path.exists(dest_path):
    os.makedirs(dest_path)
  
  # check imagemagick and wand library
  try:
    from wand.image import Image
    print('ImageMagick and Wand is available')
  except:
    print('ImageMagick and Wand is not available: please install imagemagick and wand')
  
  if '-r' in kargs:
    def get_directory(orig, path=''):
      result = []
      p = os.path.join(orig, path)
      dirs = [os.path.join(path, x) for x in os.listdir(p) if os.path.isdir(os.path.join(p, x))]
      if len(dirs) > 0:
        result = list(dirs)
        for dir in dirs:
          result += get_directory(orig, dir)
      return result
    
    directories = [''] + get_directory(orig_path)
    
  else:
    directories = ['']
  
  converted_cnt = 0
  for directory in directories:
    converted_cnt += process(orig_path, dest_path, directory, *kargs)
  
  print('Total %d files converted.' % converted_cnt)

if __name__ == '__main__':
  main()
