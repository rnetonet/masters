% ufbathesis - formato LaTeX p/ textos de trabalhos de conclusão do PGCOMP-UFBA

## Sobre

Este pacote é destinado à escrita de trabalhos de conclusão de curso,
documentos de qualificação de mestrado e de doutorado,
dissertações de mestrado e teses de doutorado da 
Universidade Federal da Bahia.

Este pacote é baseado no pacote 
[UFPEThesis] (http://www.cin.ufpe.br/~paguso/ufpethesis/), 
por Paulo G. S. da Fonseca, e em uma versão modificada para 
o DMCC por Alírio Sá e Antonio Terceiro.
Adaptado para o PGCOMP por Christina von Flach em 2014.

## Como usar

* Instale o [abnTeX] (http://code.google.com/p/abntex2/ ou 
http://www.ctan.org/pkg/abntex2).

* [Baixe o pacote/clone o projeto] pgcomp-ufba no
github (https://github.com/christinaflach/pgcomp-ufba.git).

* Use `ufbathesis` como o `documentclass` do seu documento.

* Tente seguir um dos modelos o mais fielmente possível.

* Os templates em latex apresentam a estrutura para 
msc (dissertacao de mestrado), phd (tese de doutorado),
qual (qualificacao de mestrado) e prop (qualificacao de doutorado).

* Em caso de dúvidas, olhe com cuidado os templates fornecidos e, se
necessário, o código do `ufbathesis.cls`.

* Exemplos:
   - Para compilar um documento de qualificação de mestrado 
(arquivo "template-qual.tex"), use "make qual";

   - Para compilar um documento de qualificação de doutorado
(arquivo "template-prop.tex"), use "make prop".

