# Relatório de Prontidão Omnichannel - Evo CRM Community

**Data:** 2024-05-24
**Comitê:** Winston (Arquiteto), John (PM), Sally (UX), Mary (Analista) e EVO Master.

## 1. Status Atual
O Evo CRM Community possui uma arquitetura **Multi-channel** sólida, com suporte nativo no backend para mais de 10 tipos de canais. No entanto, a experiência **Omnichannel** (integração fluida entre eles) ainda está em estágio inicial.

### Canais Identificados (Auditados):
*   **Totalmente Ativos:** WhatsApp (Evolution API/Cloud), Email, WebWidget, Telegram.
*   **Backend Pronto / Frontend Inativo:** Line, Twitter (X).
*   **Legados/Parciais:** Facebook, Instagram, SMS (Twilio).

## 2. Lacunas Críticas para Omnichannel

### A. Resolução de Identidade (Identity Resolution)
*   **Problema:** O sistema trata cada canal como um novo contato. Um cliente que entra via WhatsApp e depois via Email gera dois registros órfãos.
*   **Necessidade:** Implementar um serviço de "Merge de Contatos" baseado em atributos comuns (Telefone, Email, CPF) para unificar a timeline.

### B. Transição Fluida de Canal (Channel Switching)
*   **Problema:** Uma conversa está presa ao canal de origem.
*   **Necessidade:** Permitir que o agente de suporte mude o "canal de saída" durante um atendimento ativo. Ex: Iniciar no Chat do Site e terminar no WhatsApp.

### C. Abstração de Mensagens (Unified Message Schema)
*   **Problema:** O código contém verificações de `channel_type` espalhadas por diversos modelos e serviços, dificultando a escala.
*   **Necessidade:** Criar uma camada de drivers onde cada canal traduz sua carga específica para um formato padrão EVO.

## 3. Roadmap Recomendado

### Fase 1: Ativação e Polimento (Curto Prazo)
1.  Habilitar **Line** e **Twitter** no frontend.
2.  Implementar a visualização de ícones de canal na lista de conversas para facilitar a identificação.

### Fase 2: Unificação (Médio Prazo)
1.  Desenvolver a ferramenta de **Merge de Contatos**.
2.  Unificar as timelines de conversa (Customer Profile View v2).

### Fase 3: Expansão Estratégica (Longo Prazo)
1.  Integração com **Google Business Messages**.
2.  Integração com **Marketplaces** (Mercado Livre, Shopee).
3.  Implementação de **Shared Inbox** para múltiplos agentes com roteamento inteligente.

## 4. Conclusão dos Especialistas
A solução é altamente competitiva. O diferencial para se tornar "Omnichannel" não é apenas a quantidade de conexões, mas a inteligência de manter o contexto do cliente independente de por onde ele escolha falar.

---
*Documento compilado sob a orquestração do EVO Master.*
