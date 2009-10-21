def normalizecolor(color):
  splitcolor = [0,0,0]

  if color[0] == '#':
    color = color[1:]
  
  color = int(color,16)
  splitcolor[0] = color >> 16
  splitcolor[1] = (color >> 8)%256
  splitcolor[2] = color % 256

  maxcomp = max(splitcolor)
  if maxcomp < 127:
    brighten = 255-maxcomp
    splitcolor[0] += brighten
    splitcolor[1] += brighten
    splitcolor[2] += brighten

  color = 0
  color += splitcolor[0] << 16
  color += splitcolor[1] << 8
  color += splitcolor[2]

  color = '#'+hex(color)[2:]

  return color 
