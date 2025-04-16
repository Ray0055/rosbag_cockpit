# Access to remote server to check frontend and backend

frontend:
```bash
ssh -L 5173:172.19.0.2:5173 carmaker@10.26.18.150
```

backend:
```bash
ssh -L 8000:0.0.0.0:8000 carmaker@10.26.18.150
```

# build docker locally
use `start.sh` to build and run docker
```bash
source start.sh
```
