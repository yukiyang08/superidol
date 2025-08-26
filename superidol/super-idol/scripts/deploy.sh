#!/bin/bash

# 部署後端
cd ../backend
# source venv/bin/activate  # Linux/Mac
source venv\Scripts\activate   # Windows
python run.py &

# 部署前端
cd ../frontend
npm run build
npm run preview 