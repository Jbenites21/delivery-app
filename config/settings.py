from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    #MYSQL_USER: str = Field(..., env="MYSQL_USER")
    #MYSQL_PASSWORD: str = Field(..., env="MYSQL_PASSWORD")
    MYSQL_HOST: str = Field(..., env="MYSQL_HOST")
    MYSQL_PORT: int = Field(..., env="MYSQL_PORT")
    MYSQL_DATABASE: str = Field(..., env="MYSQL_DATABASE")
    MYSQL_ROOT_PASSWORD: str = Field(..., env="MYSQL_ROOT_PASSWORD")

    @property
    def DATABASE_URL(self) -> str:
        """Genera la URL de conexión a la base de datos MySQL"""
        return f"mysql+pymysql://root:{self.MYSQL_ROOT_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()