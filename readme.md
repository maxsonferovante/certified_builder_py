# Certified Builder Py

Sistema de geração automática de certificados para eventos usando AWS Lambda e Docker. O projeto gera certificados personalizados para participantes de eventos, processando mensagens do SQS e utilizando templates predefinidos.

[![Continuos Integration -Testing - Certified Builder Py](https://github.com/maxsonferovante/certified_builder_py/actions/workflows/workflow_testing.yaml/badge.svg)](https://github.com/maxsonferovante/certified_builder_py/actions/workflows/workflow_testing.yaml)

[![Publish Docker image to AWS ECR Private](https://github.com/maxsonferovante/certified_builder_py/actions/workflows/workflow_build.yaml/badge.svg)](https://github.com/maxsonferovante/certified_builder_py/actions/workflows/workflow_build.yaml)

## Funcionalidades

- Geração de certificados personalizados com:
  - Nome do participante em fonte estilizada
  - Código de validação único
  - Logo do evento
  - Detalhes do evento em três linhas centralizadas
  - QR Code para validação
- Processamento de mensagens SQS
- Execução em container Docker
- Deploy automatizado para AWS Lambda
- Integração com AWS ECR

## Estrutura do Projeto

```plaintext
project_root/
├── certified_builder/
│   ├── certified_builder.py    # Classe principal de geração de certificados
│   └── utils/
│       └── fetch_file_certificate.py  # Utilitário para download de imagens
├── models/
│   ├── participant.py          # Modelo de dados do participante
│   ├── certificate.py          # Modelo de dados do certificado
│   └── event.py               # Modelo de dados do evento
├── fonts/
│   ├── PinyonScript/          # Fonte para o nome do participante
│   └── ChakraPetch/           # Fonte para detalhes e código de validação
├── lambda_function.py         # Handler da função Lambda
├── Dockerfile                 # Configuração do container
└── requirements.txt           # Dependências do projeto
```

## Tecnologias Utilizadas

- Python 3.13
- Pillow (Processamento de imagens)
- httpx (Requisições HTTP)
- Pydantic (Validação de dados)
- Docker
- AWS Lambda
- AWS ECR
- AWS SQS

## Formato da Mensagem SQS

```json
{
  "participants": [
    {
      "first_name": "Nome",
      "last_name": "Sobrenome",
      "email": "email@exemplo.com",
      "phone": "(00) 00000-0000",
      "cpf": "000.000.000-00",
      "order_id": 123,
      "product_id": 456,
      "product_name": "Nome do Evento",
      "certificate_details": "Descrição do certificado em três linhas",
      "certificate_logo": "URL do logo",
      "certificate_background": "URL do template",
      "order_date": "2025-03-26 20:55:25",
      "checkin_latitude": "-27.5460492",
      "checkin_longitude": "-48.6227075",
      "time_checkin": "2025-03-26 20:55:44"
    }
  ]
}
```

## Desenvolvimento Local

### Pré-requisitos

- Docker
- Python 3.13+
- AWS CLI configurado

### Executando Localmente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/certified_builder_py.git
cd certified_builder_py
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute com Docker:
```bash
docker build -t certified-builder . && docker run -p 9000:8080 certified-builder
```

4. Teste localmente:
```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @test/mock.json
```

## Deploy

O deploy é automatizado através do GitHub Actions:

1. Push para a branch main dispara o workflow
2. Imagem Docker é construída
3. Upload para AWS ECR
4. Atualização da função Lambda

## Estrutura do Certificado Gerado

- **Logo**: Canto superior esquerdo (150x150 pixels)
- **Nome**: Centro do certificado (fonte Pinyon Script)
- **Detalhes**: Três linhas centralizadas abaixo do nome (fonte Chakra Petch)
- **Código de Validação**: Canto inferior direito (fonte Chakra Petch)
- **QR Code**: Canto inferior direito para validação online

## Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

