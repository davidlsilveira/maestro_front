# Observabilidade do Maestro Front

Este módulo adiciona métricas de aplicação ao front-end (Streamlit) usando o
[`prometheus-client`](https://github.com/prometheus/client_python). As métricas
são expostas em um endpoint HTTP dedicado para integração com Prometheus e
visualização em Grafana.

## Como funciona

- O servidor de métricas é iniciado automaticamente quando o Streamlit sobe.
- Por padrão as métricas ficam disponíveis em `http://0.0.0.0:9464/metrics`.
- É possível personalizar endereço e porta usando variáveis de ambiente:

  ```bash
  PROMETHEUS_METRICS_PORT=9464
  PROMETHEUS_METRICS_ADDR=0.0.0.0
  ```

- O módulo `observability/metrics.py` mantém contadores, histogramas e *gauges*
  para acompanhar:
  - Visualizações de páginas (menu lateral)
  - Duração de renderização de seções do Streamlit
  - Interações do usuário (ex.: clique em “Voltar para Lista” de Prompts)
  - Duração, volume e erros das operações de banco de dados
  - Abertura e falhas de conexão com o PostgreSQL
  - Timestamp da última renderização concluída sem erro

As funções de repositório utilizam o decorator `@db_operation`, o que garante
que cada chamada ao banco seja automaticamente medida. Os componentes de tela
foram encapsulados em *render functions* que usam `observe_render(...)`.

## Exemplo de configuração Prometheus

1. Crie um arquivo `prometheus.yml` com o *scrape job* apontando para o front:

   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'maestro_front'
       metrics_path: /metrics
       static_configs:
         - targets:
             - maestro-front.local:9464
   ```

   > Ajuste `maestro-front.local` para o host/IP onde o Streamlit roda dentro da
   > sua rede ou docker compose.

2. Suba Prometheus (exemplo com Docker):

   ```bash
   docker run \
     -d \
     --name prometheus \
     -p 9090:9090 \
     -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml \
     prom/prometheus
   ```

## Dashboard rápido no Grafana

1. Suba o Grafana (ou utilize o existente):

   ```bash
   docker run -d --name grafana -p 3000:3000 grafana/grafana-enterprise
   ```

2. Configure uma **Data Source** do tipo *Prometheus* apontando para
   `http://prometheus:9090` (ou o endereço adequado).

3. Crie um dashboard e utilize algumas consultas sugeridas:

   | Métrica                                   | Consulta Grafana / PromQL                                  | Observação                              |
   | ----------------------------------------- | ---------------------------------------------------------- | --------------------------------------- |
   | Page views                                | `sum(rate(maestro_streamlit_page_views_total[5m])) by (page)` | Popularidade das páginas                |
   | Duração de renderização                   | `histogram_quantile(0.95, sum(rate(maestro_streamlit_render_duration_seconds_bucket[5m])) by (le, section))` | P95 do tempo de render por seção        |
   | Operações de banco (sucesso)              | `sum(rate(maestro_db_operations_total[5m])) by (operation)` | Volume de queries                       |
   | Erros de banco                            | `sum(rate(maestro_db_operation_errors_total[5m])) by (operation)` | Monitorar falhas específicas            |
   | Duração das operações de banco            | `histogram_quantile(0.95, sum(rate(maestro_db_operation_duration_seconds_bucket[5m])) by (le, operation))` | P95 das operações mais lentas           |
   | Última renderização concluída             | `time() - maestro_streamlit_last_success_timestamp`        | Alerta se ficar *stale* por muito tempo |

4. Configure alertas, por exemplo:

   - Página sem renderizar há mais de 10 minutos.
   - Taxa de erro de banco acima de `0.05` por operação.
   - Tempo P95 de renderização acima de 2 segundos.

## Boas práticas adicionais

- Centralize a definição de novos eventos de UI em `observability/metrics.py`
  para manter nomes consistentes.
- Ao criar novos repositórios ou chamadas intensivas a APIs, reutilize o
  decorator `@db_operation` ou crie variantes específicas conforme necessário.
- Em ambiente produtivo, exponha as métricas em uma rede interna ou protegida,
  pois o endpoint não possui autenticação.

## Verificação rápida

1. Execute o front normalmente:

   ```bash
   streamlit run app.py
   ```

2. Em outro terminal, faça uma requisição ao endpoint de métricas:

   ```bash
    curl http://localhost:9464/metrics
   ```

   Você deve enxergar contadores como `maestro_streamlit_page_views_total` e
   histogramas `maestro_db_operation_duration_seconds_bucket`.
