# Create helper directory
import os
os.makedirs('helper', exist_ok=True)

# Create __init__.py
with open('helper/__init__.py', 'w') as f:
    f.write('"""Helper modules for PhysioSOAP workflow."""\n')
