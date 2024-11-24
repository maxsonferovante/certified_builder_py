## Certificado Automático com Python: Gerador de Certificados

Este projeto é um sistema de geração automática de certificados personalizados para participantes de eventos, utilizando **Python**, **Pillow**, **httpx** e uma integração com uma API externa. Agora, além de gerar os certificados localmente, ele envia os certificados gerados diretamente para um endpoint remoto.

---

### Estrutura do Projeto

O projeto contém os seguintes componentes principais:

1. **`EventsAPI`**: Classe responsável por:
   - Buscar a lista de participantes via API.
   - Fazer download do template do certificado.
   - Enviar o certificado gerado para o servidor.

2. **`Participant`**: Modelo que representa os dados de um participante do evento.

3. **`CertifiedBuilder`**: Classe principal que:
   - Gera certificados personalizados para cada participante.
   - Realiza o upload dos certificados gerados para a API.

4. **Pasta de Fontes** (`fonts/static/OpenSans-Regular.ttf`): Fonte usada para escrever o nome no certificado.

5. **Pasta de Saída** (`certificates/`): Certificados gerados localmente.

---

### Novas Funcionalidades

1. **Integração com API para Upload de Certificados**:
   - Após gerar o certificado, ele é convertido para um objeto binário em memória e enviado para a API utilizando a biblioteca **httpx**.

2. **Download Dinâmico do Template do Certificado**:
   - O template do certificado é baixado diretamente de uma URL fornecida pela API e salvo localmente para uso.

3. **Envio Dinâmico dos Certificados**:
   - Os certificados gerados são enviados para a API de upload junto com os dados do participante, como nome, e-mail, e código de validação.

---

### Explicação do Código

#### **`EventsAPI`**

- **Objetivo**: Fornecer métodos para integração com a API de eventos.

1. **`fetch_participants()`**:
   - Faz uma requisição `GET` para buscar a lista de participantes.
   - Transforma os dados recebidos em instâncias da classe `Participant`.

2. **`fetch_file_certificate()`**:
   - Faz o download do template de certificado de uma URL fornecida pela API.
   - Retorna o template como um objeto **Pillow Image**.

3. **`save_certificate(image_buffer, participant)`**:
   - Envia o certificado gerado para a API de upload.
   - Os dados do participante são enviados no corpo da requisição e a imagem é enviada como um arquivo no formato `multipart/form-data`.

---

#### **`CertifiedBuilder`**

- **Objetivo**: Gerenciar a criação e envio de certificados personalizados.

1. **`build_certificates()`**:
   - Obtém a lista de participantes da API e o template do certificado.
   - Para cada participante:
     - Gera o certificado personalizado.
     - Salva o certificado localmente e envia para a API de upload.

2. **`generate_certificate(participant, certificate_template)`**:
   - Adiciona o nome do participante centralizado ao template do certificado.
   - Retorna a imagem gerada para ser usada no upload.

3. **`create_name_image(name, size)`**:
   - Cria uma imagem com o nome do participante centralizado.
   - Usa o método `calculate_text_position()` para determinar a posição exata.

4. **`save_certificate(certificate, participant)`**:
   - Converte o certificado gerado em um buffer de memória.
   - Envia o certificado para a API de upload por meio do método `save_certificate()` da `EventsAPI`.

---

### Como Funciona o Fluxo

1. **Busca de Participantes e Template**:
   - A API retorna a lista de participantes e o template do certificado.

2. **Geração do Certificado**:
   - O nome do participante é renderizado no template.
   - A imagem é gerada e salva localmente.

3. **Upload para o Servidor**:
   - O certificado é enviado diretamente para o endpoint da API com os dados do participante.

---

### Exemplo de Uso

**1. Configuração Inicial**

Certifique-se de que:
- A API está configurada e retornando os dados corretamente.
- O diretório `certificates/` existe:
  ```bash
  mkdir certificates
  ```

- A fonte utilizada (`OpenSans-Regular.ttf`) está na pasta `fonts/static/`.

**2. Execução**

Execute o script principal:

```bash
python main.py
```

O script irá:
1. Buscar os participantes.
2. Fazer download do template do certificado.
3. Gerar os certificados personalizados.
4. Salvar os certificados localmente.
5. Enviar os certificados para a API.

---

### Dependências

Instale as dependências necessárias com:

```bash
pip install pillow httpx
```

---

### Saída Esperada

- Certificados personalizados serão gerados e salvos no diretório `certificates/`.
- Os certificados gerados serão enviados com sucesso para a API.

---

### Estrutura do Diretório

```plaintext
project_root/
├── certified_builder/
│   ├── certified_builder.py    # Classe para gerar certificados
├── events_api/
│   ├── events_api.py           # Integração com a API de eventos
│   ├── models/
│       ├── participant.py      # Modelo do participante
├── certificates/               # Diretório para salvar os certificados gerados
├── fonts/
│   ├── static/
│       ├── OpenSans-Regular.ttf # Fonte utilizada
├── main.py                     # Script principal para execução
├── README.md                   # Documentação do projeto
```

---

### Conclusão

Este projeto demonstra como integrar dados dinâmicos a templates de imagem para criar certificados personalizados e enviá-los para uma API. É uma solução prática e escalável para eventos, automatizando tanto a geração quanto o upload dos certificados.

