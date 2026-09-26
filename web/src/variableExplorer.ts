/** Searchable bilingual INEC dictionary controls, loaded only when opened. */
import type { Level } from './indicatorMaps'

export interface CensusCategory {
  id: number
  code: string
  label: { es: string; en: string }
  label_source?: string
  midpoint?: number
}
export interface CensusVariable {
  id: string
  table: string
  theme: string
  name: { es: string; en: string }
  question: { es: string; en: string }
  type: 'categorical' | 'numeric'
  universe: { es: string; en: string; denominator: string }
  min_level: Level
  available: boolean
  categories: CensusCategory[]
}
export type VariableMode = 'percent' | 'count' | 'density' | 'mean'
export interface VariableChoice {
  variable: CensusVariable
  category: CensusCategory | null
  mode: VariableMode
}

const labels = {
  es: { indicators: 'Indicadores', variables: 'Variables del censo',
    search: 'Buscar código, nombre o pregunta · techo, internet, idioma…',
    table: 'Tabla', all: 'Todas las tablas', variable: 'Variable',
    category: 'Categoría', mode: 'Mapa', percent: '% del universo',
    count: 'Conteo', density: 'Por km²', mean: 'Media',
    question: 'Pregunta original', universe: 'Universo',
    unavailable: 'Sin agregado público', loading: 'Cargando catálogo del INEC…' },
  en: { indicators: 'Indicators', variables: 'Census variables',
    search: 'Search code, name or question · roof, internet, language…',
    table: 'Table', all: 'All tables', variable: 'Variable',
    category: 'Category', mode: 'Map', percent: '% of universe',
    count: 'Count', density: 'Per km²', mean: 'Mean',
    question: 'Original question', universe: 'Universe',
    unavailable: 'No public aggregate', loading: 'Loading INEC catalog…' },
}
const themeEN: Record<string, string> = {
  'Diáspora': 'Diaspora', 'Mortalidad': 'Mortality',
  'Vivienda y servicios': 'Housing and services',
  'Conectividad y equipamiento': 'Connectivity and equipment',
  'Movilidad y memoria familiar': 'Mobility and family history',
  'Hogar': 'Households', 'Educación': 'Education',
  'Brecha digital': 'Digital divide', 'Trabajo': 'Work',
  'Fecundidad': 'Fertility', 'Diversidad': 'Diversity',
  'Movilidad interna': 'Internal mobility', 'Población': 'Population',
}
const tableEN: Record<string, string> = {
  vivienda: 'Dwelling', hogar: 'Household', poblacion: 'Population',
  emigracion: 'Emigration', mortalidad: 'Mortality',
}
const normalize = (text: string): string => text.normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '').toLowerCase()

export function mountVariableExplorer(base: string, onChange: (choice: VariableChoice | null) => void,
                                      onTab: (tab: 'indicators' | 'variables') => void) {
  const container = document.querySelector<HTMLElement>('#variable-pane')!
  const search = document.querySelector<HTMLInputElement>('#variable-search')!
  const table = document.querySelector<HTMLSelectElement>('#variable-table')!
  const select = document.querySelector<HTMLSelectElement>('#variable-select')!
  const category = document.querySelector<HTMLSelectElement>('#variable-category')!
  const mode = document.querySelector<HTMLSelectElement>('#variable-mode')!
  const details = document.querySelector<HTMLElement>('#variable-details')!
  const tabs = Array.from(document.querySelectorAll<HTMLButtonElement>('.explorer-tab'))
  let language: 'es' | 'en' = 'es'
  let variables: CensusVariable[] = []
  let current: CensusVariable | null = null
  let loaded: Promise<void> | null = null
  let activeTab: 'indicators' | 'variables' = 'indicators'

  function choice(): VariableChoice | null {
    if (!current) return null
    return { variable: current,
      category: current.type === 'categorical'
        ? current.categories.find(item => String(item.id) === category.value) ?? null : null,
      mode: current.type === 'numeric' ? 'mean' : mode.value as VariableMode }
  }
  function renderSelected(preserve = true) {
    const t = labels[language]
    const oldCategory = preserve ? category.value : ''
    const oldMode = preserve ? mode.value : ''
    category.replaceChildren()
    if (!current) { details.replaceChildren(); return }
    for (const item of current.categories) category.add(new Option(
      `${item.code} · ${item.label[language]}`, String(item.id)))
    if (oldCategory && Array.from(category.options).some(item => item.value === oldCategory)) {
      category.value = oldCategory
    }
    category.hidden = current.type === 'numeric'
    document.querySelector<HTMLElement>('#variable-category-label')!.hidden = category.hidden
    mode.replaceChildren()
    const choices: [VariableMode, string][] = current.type === 'numeric'
      ? [['mean', t.mean]] : [['percent', t.percent], ['count', t.count], ['density', t.density]]
    for (const [value, label] of choices) mode.add(new Option(label, value))
    if (oldMode && Array.from(mode.options).some(item => item.value === oldMode)) mode.value = oldMode
    const question = document.createElement('p')
    question.textContent = `${t.question}: ${current.question[language]}`
    const universe = document.createElement('p')
    universe.textContent = `${t.universe}: ${current.universe[language]}`
    details.replaceChildren(question, universe)
    const codeOnly = current.type === 'categorical' && current.categories.some(item =>
      item.label_source === 'código INEC')
    if (codeOnly) {
      const note = document.createElement('p')
      note.textContent = language === 'es'
        ? 'Algunas categorías muestran el código oficial: el diccionario verificado no trae su etiqueta.'
        : 'Some categories show the official code: the verified dictionary has no label.'
      details.append(note)
    }
    if (current.id === 'P03') {
      const note = document.createElement('p')
      note.textContent = language === 'es'
        ? 'Media aproximada a partir de grupos quinquenales; 100–120 usa punto medio 110.'
        : 'Approximate mean from five-year age groups; 100–120 uses midpoint 110.'
      details.append(note)
    }
  }
  function renderList() {
    const query = normalize(search.value.trim())
    const selected = current?.id ?? ''
    select.replaceChildren()
    select.add(new Option(language === 'es' ? 'Elige una variable' : 'Choose a variable', ''))
    const groups = new Map<string, HTMLOptGroupElement>()
    for (const variable of variables) {
      if (table.value && variable.table !== table.value) continue
      const words = `${variable.id} ${variable.name.es} ${variable.name.en} `
        + `${variable.question.es} ${variable.question.en}`
      if (query && !normalize(words).includes(query)) continue
      const theme = language === 'en' ? themeEN[variable.theme] ?? variable.theme : variable.theme
      let group = groups.get(theme)
      if (!group) {
        group = document.createElement('optgroup')
        group.label = theme
        select.add(group)
        groups.set(theme, group)
      }
      const option = new Option(`${variable.id} · ${variable.name[language]}`, variable.id)
      option.disabled = !variable.available
      option.title = !variable.available ? labels[language].unavailable : ''
      group.append(option)
    }
    select.value = selected && Array.from(select.options).some(option => option.value === selected)
      ? selected : ''
  }
  async function load() {
    if (!loaded) {
      loaded = (async () => {
        container.dataset.status = labels[language].loading
        const response = await fetch(`${base}meta/variables.json`)
        if (!response.ok) throw new Error(`INEC variable catalog: ${response.status}`)
        const catalog = await response.json() as { variables: CensusVariable[] }
        variables = catalog.variables
        renderList()
        delete container.dataset.status
      })()
    }
    await loaded
  }
  async function setTab(tab: 'indicators' | 'variables') {
    activeTab = tab
    for (const button of tabs) {
      const active = button.dataset.tab === tab
      button.setAttribute('aria-selected', String(active))
      button.classList.toggle('active', active)
    }
    document.querySelector<HTMLElement>('#indicator-pane')!.hidden = tab !== 'indicators'
    container.hidden = tab !== 'variables'
    onTab(tab)
    if (tab === 'variables') await load()
  }
  for (const button of tabs) button.addEventListener('click', () => {
    void setTab(button.dataset.tab as 'indicators' | 'variables')
  })
  search.addEventListener('input', renderList)
  table.addEventListener('change', renderList)
  select.addEventListener('change', () => {
    current = variables.find(item => item.id === select.value) ?? null
    renderSelected(false)
    onChange(choice())
  })
  category.addEventListener('change', () => onChange(choice()))
  mode.addEventListener('change', () => onChange(choice()))
  return {
    get tab() { return activeTab },
    render(lang: 'es' | 'en') {
      language = lang
      const t = labels[lang]
      tabs[0].textContent = t.indicators
      tabs[1].textContent = t.variables
      search.placeholder = t.search
      document.querySelector<HTMLElement>('#variable-table-label')!.textContent = t.table
      document.querySelector<HTMLElement>('#variable-select-label')!.textContent = t.variable
      document.querySelector<HTMLElement>('#variable-category-label')!.textContent = t.category
      document.querySelector<HTMLElement>('#variable-mode-label')!.textContent = t.mode
      table.replaceChildren(new Option(t.all, ''))
      for (const name of ['vivienda', 'hogar', 'poblacion', 'emigracion', 'mortalidad']) {
        table.add(new Option(lang === 'es' ? name : tableEN[name], name))
      }
      renderList()
      renderSelected()
    },
    selectVariable(id: string, categoryId?: number, chosenMode?: VariableMode) {
      void setTab('variables').then(() => {
        select.value = id
        current = variables.find(item => item.id === id) ?? null
        renderSelected(false)
        if (categoryId != null) category.value = String(categoryId)
        if (chosenMode) mode.value = chosenMode
        onChange(choice())
      })
    },
  }
}
