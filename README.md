# GSASEC

Portfólio e site de serviços de Giovanni S. Alves, publicado em https://gsasec.com.br/ pelo GitHub Pages. HTML, CSS e JavaScript estáticos; não há instalação de pacotes ou etapa de build.

## Prévia local

Na raiz do repositório, com Python 3.9 ou superior:

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Abra http://127.0.0.1:8765/ e use Ctrl+C para encerrar o servidor.

## Páginas e manutenção

- `index.html`: serviços, acesso ao portfólio e contato.
- `src/cases.html`: investigações e PDFs.
- `src/projeto_automacao.html`: cyber hygiene, relatórios, coleta forense e Shadow IT.
- `src/projeto_threathunting.html`: estudos de detecção.
- `src/projeto_malwarelab.html`: laboratório e apresentações no LinkedIn.
- `src/sobre.html`: biografia, certificações e contato.
- `css/site.css`: estilos compartilhados e responsividade.
- `js/main.js`: menu acessível e analytics, carregado apenas no domínio de produção.

O cabeçalho e o rodapé são HTML estático em cada página, para manter a navegação disponível mesmo sem JavaScript. Ao mudar um item do menu ou um contato, atualize as seis páginas principais. Atualize o parâmetro de versão do `main.js` quando modificar esse arquivo, evitando caches antigos no navegador.

O site contém somente as seis páginas principais, todas listadas no sitemap. As páginas antigas de compatibilidade foram removidas; seus endereços passam a retornar 404 após a publicação. Os arquivos dos relatórios e as imagens originais permanecem em `pdfs/` e `img/`.

### Materiais em preparação

Quando não houver material publicado, use um `<span class="content-unavailable">Código · Conteúdo em preparação</span>`. Quando o arquivo ou publicação estiver disponível, substitua por um link real. Não use `href="#"`. O print do coletor é identificado como imagem da coleta; o relatório de cyber hygiene é identificado como exemplo, sem ser apresentado como manual ou código-fonte.

## Verificação

```sh
python scripts/validate_site.py
python scripts/validate_site.py --base-url http://127.0.0.1:8765/
node --check js/main.js
```

O validador usa apenas a biblioteca padrão do Python. Verifica rotas, links locais, âncoras, arquivos, contatos, metadados, sitemap e referências de acessibilidade. A opção `--base-url` também verifica os recursos por HTTP; não testa sites externos.

Antes de publicar, confira as seis páginas em desktop, tablet e celular; abra o menu, navegue por teclado e feche com Escape. Atualize `lastmod` no sitemap quando o conteúdo mudar.

## Publicação

O `CNAME` continua apontando para `gsasec.com.br`. Faça a revisão do diff e o push conforme o fluxo do repositório no GitHub Pages. Não há configuração do Sites ou novo serviço de hospedagem.
