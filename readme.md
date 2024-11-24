## Certificado Automático com Python: Gerador de Certificados

Este projeto é um sistema de geração automática de certificados personalizados para participantes de eventos, utilizando **Python**, **Pillow** e uma integração com uma API de eventos. Abaixo está uma explicação detalhada sobre o código e como ele funciona.

---

### Estrutura do Projeto

O projeto contém os seguintes componentes principais:

1. **`EventsAPI`**: Classe responsável por buscar os dados dos participantes e o template do certificado.
2. **`Participant`**: Modelo que representa os dados de um participante do evento.
3. **`CertifiedBuilder`**: Classe principal que gerencia a criação e personalização dos certificados.
4. **Pasta de Fontes** (`fonts/static/OpenSans-Regular.ttf`): Fonte usada para escrever o nome no certificado.
5. **Saída**: Certificados gerados são salvos na pasta `certificates`.

---

### Explicação do Código

#### **`CertifiedBuilder`**

- **Objetivo**: Gerar certificados personalizados para cada participante utilizando os templates fornecidos pela API.
  
1. **`__init__`**:
   - Inicializa o construtor, recebendo a API de eventos como parâmetro.

2. **`build_certificates()`**:
   - Busca a lista de participantes por meio da API (`self.events_api.fetch_participants()`).
   - Para cada participante, faz o seguinte:
     - Busca o template do certificado usando a API (`self.events_api.fetch_file_certificate()`).
     - Gera o certificado personalizado usando `generate_certificate()`.

3. **`generate_certificate(participant, certificate_template)`**:
   - Cria uma imagem com o nome do participante chamando `create_name_image()`.
   - Insere o nome do participante no template utilizando o método `paste()` da PIL.
   - Salva o certificado no diretório `certificates/` com o nome do participante.

4. **`create_name_image(name, size)`**:
   - Cria uma nova imagem transparente para o nome do participante.
   - Calcula a posição central do texto no certificado com o método `calculate_text_position()`.
   - Escreve o nome na imagem usando a biblioteca **Pillow**.

5. **`calculate_text_position(text, font, draw, size)`**:
   - Calcula as dimensões do texto usando o método `textbbox()` da PIL.
   - Determina a posição central do texto com base no tamanho da imagem e no texto.

---

### Como Funciona o Fluxo

1. **Obtenção de Participantes**:
   - Os dados dos participantes são obtidos a partir da classe `EventsAPI`.

2. **Template do Certificado**:
   - Para cada participante, um template de certificado é buscado via API.

3. **Geração do Certificado**:
   - O nome do participante é desenhado centralizado na imagem do template.
   - O certificado final é salvo no diretório `certificates/`.

---

### Exemplo de Uso

**1. Configuração Inicial**

- Certifique-se de que a API está disponível e retorna os dados necessários:
  - Lista de participantes.
  - Template do certificado.

- Certifique-se de que o diretório `certificates/` existe:
  ```bash
  mkdir certificates
  ```

- Certifique-se de que a fonte usada está na pasta `fonts/static/`.

**2. Execução**

Execute o script principal:

```bash
python main.py
```

O script irá:
1. Buscar participantes.
2. Gerar certificados personalizados.
3. Salvar os certificados na pasta `certificates/`.

---

### Dependências

Este projeto utiliza as seguintes dependências:

- **Pillow**: Biblioteca para manipulação de imagens.
- **EventsAPI**: API fictícia usada para buscar participantes e templates.

Instale as dependências necessárias:

```bash
pip install pillow
```

---

### Saída Esperada

Certificados serão gerados e salvos no formato PNG no diretório `certificates/`, com o nome dos participantes centralizado no template.

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


### Conclusão

Este projeto demonstra como integrar dados dinâmicos a templates de imagem para criar certificados personalizados, utilizando Python e a biblioteca Pillow. É uma solução prática para eventos, automatizando a geração de certificados de forma eficiente e escalável.