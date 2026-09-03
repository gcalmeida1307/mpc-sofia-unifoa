// Visual metadata only. Documents and counts always come from the local API
// scanning the physical knowledge/ directory.
export type KnowledgeModule = {
  id: string
  name: string
  icon: string
  color: string
  category: string
  docs: string
  queries: string
  accuracy: string
  greeting: string
  manager: string
  focus: string
  documentsByType?: Record<string, number>
  links?: number
  linkStorage?: string
}

export const knowledgeModules: KnowledgeModule[] = [
  { id: 'almoxarifado', name: 'Almoxarifado', icon: '▣', color: '#818cf8', category: 'Operações', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso ajudar com estoque, materiais e movimentações.', manager: 'Gestor de estoque', focus: 'Materiais, inventário, compras e movimentações.' },
  { id: 'contabilidade', name: 'Contabilidade', icon: '▤', color: '#f59e0b', category: 'Finanças', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar fechamentos, lançamentos e conformidade contábil.', manager: 'Gestor contábil', focus: 'Lançamentos, conformidade, fechamentos e indicadores.' },
  { id: 'departamento-pessoal', name: 'Departamento Pessoal', icon: '♙', color: '#f472b6', category: 'Pessoas', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar rotinas trabalhistas e políticas internas.', manager: 'Gestor de pessoal', focus: 'Rotinas trabalhistas, admissões, férias e folha.' },
  { id: 'direito', name: 'Direito', icon: '⚖', color: '#a78bfa', category: 'Jurídico', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso relacionar leis, normas e documentos jurídicos disponíveis.', manager: 'Gestor jurídico', focus: 'Leis, normas, conexões entre dispositivos e riscos.' },
  { id: 'financeiro', name: 'Financeiro', icon: '▥', color: '#fbbf24', category: 'Finanças', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar fluxo de caixa, custos e cenários financeiros.', manager: 'Gestor financeiro', focus: 'Fluxo de caixa, orçamento, custos e cenários.' },
  { id: 'gestao-empresarial', name: 'Gestão Empresarial', icon: '▤', color: '#fb923c', category: 'Gestão', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar processos, metas, riscos e melhoria contínua.', manager: 'Gestor executivo', focus: 'Processos, metas, riscos e melhoria contínua.' },
  { id: 'infraestrutura', name: 'Infraestrutura', icon: '⌂', color: '#22d3ee', category: 'Tecnologia', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso ajudar com redes, Zabbix, sistemas operacionais e disponibilidade.', manager: 'Gestor de infraestrutura', focus: 'Redes, Zabbix, sistemas operacionais, segurança e disponibilidade.' },
  { id: 'medicina', name: 'Medicina', icon: '✚', color: '#34d399', category: 'Saúde', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso auxiliar com protocolos, literatura e dados clínicos autorizados.', manager: 'Gestor clínico', focus: 'Protocolos, literatura, indicadores populacionais e interoperabilidade FHIR.' },
  { id: 'prefeitura', name: 'Prefeitura', icon: '⌂', color: '#60a5fa', category: 'Administração Pública', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar serviços públicos, contratos e prestação de contas.', manager: 'Gestor público', focus: 'Serviços públicos, legislação, contratos e prestação de contas.' },
  { id: 'recursos-humanos', name: 'Recursos Humanos', icon: '♟', color: '#fb7185', category: 'Pessoas', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso apoiar pessoas, desenvolvimento, clima e indicadores.', manager: 'Gestor de RH', focus: 'Pessoas, desenvolvimento, clima, políticas e indicadores.' },
  { id: 'secretaria', name: 'Secretaria', icon: '▱', color: '#c084fc', category: 'Administrativo', docs: '0', queries: '-', accuracy: '-', greeting: 'Posso organizar documentos, atendimento, agendas e fluxos.', manager: 'Gestor administrativo', focus: 'Documentos, atendimento, agendas e fluxos administrativos.' },
]
