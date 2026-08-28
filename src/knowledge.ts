export type KnowledgeModule = {
  id: string
  folder: string
  name: string
  icon: string
  color: string
  category: string
  docs: string
  queries: string
  accuracy: string
  greeting: string
}

// The knowledge directory is the source of truth for RAG modules.
// Vite bundles the files at build time and updates this manifest during dev.
const knowledgeFiles = import.meta.glob('../knowledge/**/*', {
  eager: true,
  query: '?raw',
  import: 'default',
})

const definitions = [
  { folder: 'almoxarifado', name: 'Almoxarifado', icon: '▣', color: '#818cf8', category: 'Operações', greeting: 'Posso ajudar com estoque, materiais e movimentações.' },
  { folder: 'gestao-empresarial', name: 'Gestão Empresarial', icon: '▤', color: '#fbbf24', category: 'Gestão', greeting: 'Posso ajudar com processos, indicadores e gestão empresarial.' },
  { folder: 'infraestrutura', name: 'Infraestrutura', icon: '⌂', color: '#22d3ee', category: 'Tecnologia', greeting: 'Posso ajudar com infraestrutura, redes e operações técnicas.' },
  { folder: 'medicina', name: 'Medicina', icon: '✚', color: '#34d399', category: 'Saúde', greeting: 'Posso auxiliar com protocolos e literatura médica.' },
]

export const knowledgeModules: KnowledgeModule[] = definitions.map((definition) => {
  const prefix = `../knowledge/${definition.folder}/`
  const count = Object.keys(knowledgeFiles).filter((file) => file.startsWith(prefix) && !file.endsWith('/.gitkeep')).length

  return {
    id: definition.folder,
    ...definition,
    docs: count.toLocaleString('pt-BR'),
    queries: '-',
    accuracy: '-',
  }
})
