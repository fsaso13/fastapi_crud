from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#SECRET_KEY
SECRET_KEY = settings.secret_key
#Algorithm
ALGORITHM = settings.algorithm
#Expiration Time
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.token_exp)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        deco_id: str = payload.get("user_id")
        # print(deco_id)
        if deco_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=str(deco_id))
    except JWTError:
        raise credentials_exception
    
    return token_data
    
def get_current_User(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})

    tok = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == tok.id).first()
    print(user.email)
    return user