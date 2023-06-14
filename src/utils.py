import os

"""
Helper functions
"""
def save_plot(plt, dir, filename, dummy):
  if not os.path.exists(dir):
    os.makedirs(dir)
  plt.savefig(f'{dir}{filename}')
  plt.close()

def save_image(img, dir, filename, dummy):
  if not os.path.exists(dir):
    os.makedirs(dir)
  img.save(f'{dir}{filename}')
