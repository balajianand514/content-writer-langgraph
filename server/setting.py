
# Imports for settings and configurations
from typing import Union, Callable
from starlette.config import Config
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AzureKeyCredential
from pathlib import Path
import os
from dotenv import dotenv_values
from collections import ChainMap
from azure.cosmos import CosmosClient, DatabaseProxy
from azure.mgmt.cosmosdb import CosmosDBManagementClient


class BaseSettings(Config):
    def __init__(self, env_file, env_prefix) -> None:
        environ = os.environ.copy()
        environ = ChainMap(environ, self._load_env_file(env_file))
        self.azure_subscription_id = environ.get('AZURE_SUBSCRIPTION_ID')
        self.azure_resource_group = environ.get('AZURE_RG_NAME')
        self.environment = environ.get('ENVIRONMENT')
        self.vault_url = environ.get('AZURE_VAULT_URL')
        # self.key_vault = self._get_vault()
        self.llm_config_list = [{
            "model": os.environ["AZURE_OPENAI_DEPLOYMENT_NAME_GPT4"],  # Azure deployment name
            "api_key": os.environ["AZURE_OPENAI_API_KEY"],
            "base_url": os.environ["AZURE_OPENAI_ENDPOINT"],
            "api_type": "azure",
            "api_version": os.environ["AZURE_OPENAI_API_VERSION"],  # Optional, ensure this matches your Azure API version
            # "response_format": { "type": "json_object" }
        }]
    
        super().__init__(environ=environ, env_prefix=env_prefix)

    # def _get_vault(self):
    #     credential = DefaultAzureCredential()
    #     return SecretClient(vault_url=self.vault_url, credential=credential)

    def _load_env_file(self, env_file):
        env_vars = {}
        if os.path.exists(env_file):
            env_vars.update(dotenv_values(env_file))
        return env_vars


class AzureCosmosNOSqlDBSettings(BaseSettings):
    def __init__(self) -> None:
        self.timeout = 12000
        super().__init__('.env', env_prefix='COSMOSDB_NOSQL_')

    @property
    def client(self) -> CosmosClient:
        return CosmosClient(url=self.server, credential=self.credential)

    @property
    def mgmt_client(self) -> CosmosDBManagementClient:
        return CosmosDBManagementClient(self.credential, self.azure_subscription_id)

    @property
    def db(self) -> DatabaseProxy:
        return self.client.get_database_client(self.database_name)

    @property
    def server(self) -> str:
        return self('SERVER', cast=str)

    @property
    def credential(self) -> Union[AzureKeyCredential, DefaultAzureCredential]:
        return DefaultAzureCredential()

    @property
    def database_name(self) -> str:
        return self('DB_NAME', cast=str)

    @property
    def account_name(self) -> str:
        return self('ACCOUNT_NAME', cast=str, default=Path(self.server).stem.split('.')[0])

    @property
    def chat_container_name(self) -> str:
        return self('CHAT_CONTAINER_NAME', cast=str)

    @property
    def platform_usage_container_name(self) -> str:
        return self('PLATFORM_USAGE_CONTAINER_NAME', cast=str)

    @property
    def token_usage_container_name(self) -> str:
        return self('TOKEN_USAGE_CONTAINER_NAME', cast=str)


class ApiSettings(BaseSettings):
    def __init__(self) -> None:
        self.timeout = 12000
        super().__init__('.env', env_prefix='API_')

    @property
    def port(self) -> str:
        return self('HOST', cast=int, default=8001)

    @property
    def host(self) -> str:
        return self('HOST', cast=str, default=f'https://localhost:{self.port}')

    @property
    def session_secret(self) -> str:
        return self('SESSION_SECRET', cast=str, default='ALongRandomlyGeneratedString')


class OAuthSettings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='OIDC_')

    @property
    def client_id(self) -> str:
        return self('CLIENT_ID', cast=str)

    @property
    def issuer(self) -> str:
        return self('ISSUER', cast=str)

    @property
    def metadata_uri(self) -> str:
        return f'{self.issuer}/.well-known/openid-configuration'

    @property
    def userinfo_uri(self) -> str:
        return f'{self.issuer}/idp/userinfo.openid'

    @property
    def introspect_uri(self) -> str:
        return f"{self.issuer}/as/introspect.oauth2"


class AzureOpenaiSettings(BaseSettings):
    def __init__(self) -> None:
        self.timeout = 12000
        super().__init__('.env', env_prefix='AZURE_OPENAI_')

    @property
    def credential(self) -> Union[AzureKeyCredential, DefaultAzureCredential]:
        return DefaultAzureCredential()

    @property
    def token_provider(self) -> Callable:
        return get_bearer_token_provider(
            self.credential, "https://cognitiveservices.azure.com/.default"
        )

    @property
    def endpoint(self) -> str:
        return self('ENDPOINT', cast=str)

    @property
    def version(self) -> str:
        return self('VERSION', cast=str)

    @property
    def core_chat_deployment_name(self) -> str:
        return self('CORE_CHAT_DEPLOYMENT_NAME', cast=str)

    @property
    def support_chat_deployment_name(self) -> str:
        return self('SUPPORT_CHAT_DEPLOYMENT_NAME', cast=str)

    @property
    def embedding_deployment_name(self) -> str:
        return self('EMBEDDING_DEPLOYMENT_NAME', cast=str)

    @property
    def temperature(self) -> str:
        return self('TEMPERATURE', cast=float)


class AzureDocAISettings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='AZURE_DOCAI_')

    @property
    def endpoint(self) -> str:
        return self('ENDPOINT', cast=str)

    @property
    def api_version(self) -> str:
        return self('API_VERSION', cast=str)

    @property
    def credential(self) -> Union[AzureKeyCredential, DefaultAzureCredential]:
        return DefaultAzureCredential()


class AzureAISearchSettings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='AZURE_SEARCH_')

    @property
    def endpoint(self) -> str:
        return self('ENDPOINT', cast=str)

    @property
    def index_name(self) -> str:
        return self('INDEX_NAME', cast=str)

    @property
    def credential(self) -> Union[AzureKeyCredential, DefaultAzureCredential]:
        return DefaultAzureCredential()


class AzureAppInsightsSettings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='AZURE_INSIGHTS_')

    @property
    def credential(self) -> Union[AzureKeyCredential, DefaultAzureCredential]:
        return ''

    @property
    def connection_string(self) -> str:
        return self('CONNECTION_STRING', cast=str)


class AzureSettings():
    def __init__(self) -> None:
        self._openai = AzureOpenaiSettings()
        self._cosmos_nosql = AzureCosmosNOSqlDBSettings()
        self._doc_ai = AzureDocAISettings()
        self._search = AzureAISearchSettings()
        self._insights = AzureAppInsightsSettings()
        self._bing = AzureBingSearchSettings()

    @property
    def openai(self) -> AzureOpenaiSettings:
        return self._openai

    @property
    def cosmos_nosql(self) -> AzureCosmosNOSqlDBSettings:
        return self._cosmos_nosql

    @property
    def doc_ai(self) -> AzureDocAISettings:
        return self._doc_ai

    @property
    def search(self) -> AzureAISearchSettings:
        return self._search

    @property
    def insights(self) -> AzureAppInsightsSettings:
        return self._insights


class AzureBingSearchSettings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='AZURE_BING_SEARCH_')

    @property
    def endpoint(self) -> str:
        return self('END_POINT', cast=str)
    
    @property
    def subscription_key(self) -> str:
        return self('SUBSCRIPTION_KEY', cast=str)


class Settings(BaseSettings):
    def __init__(self) -> None:
        super().__init__('.env', env_prefix='')
        self._azure = AzureSettings()
        self._api = ApiSettings()
        self._oauth = OAuthSettings()
        self.FALLBACK_MESSAGE = "Oops! Something went wrong (Error Code: {error_code}). Please try again later."

    @property
    def log_level(self) -> str:
        return self('LOG_LEVEL').upper()

    @property
    def rate_limit_cooldown(self) -> int:
        return self('RATE_LIMIT_COOLDOWN_IN_HRS', cast=int)

    @property
    def whitelisted_ad_group(self) -> str:
        return self('WHITELISTED_AD_GROUP')

    @property
    def spa_uri(self) -> str:
        return self('SPA_URI', cast=str, default='http://localhost:5173/')

    @property
    def api(self) -> ApiSettings:
        return self._api

    @property
    def azure(self) -> AzureSettings:
        return self._azure

    @property
    def oauth(self) -> OAuthSettings:
        return self._oauth

 


SETTINGS = Settings()