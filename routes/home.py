from fastapi import APIRouter

router = APIRouter()

@router.get('/home')
def get_home():
	return 'home'
