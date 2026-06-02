import { baseUrl } from 'src/boot/api'
import type { RewardDocument } from 'src/models'

const authStore = useAuthStore()

export const useRewards = defineStore('rewards', () => {
  async function downloadReward(doc: RewardDocument) {
    if (doc.id === undefined) return
    await authStore.updateToken()
    const config = {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    }
    const resp = await fetch(`${baseUrl}/reward/${doc.id}/_download`, config)
    if (!resp.ok) throw new Error(`Download failed: ${resp.statusText}`)
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.target = '_blank'
    link.rel = 'noopener noreferrer'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  async function deleteReward(doc: RewardDocument) {
    if (doc.id === undefined) return
    await authStore.updateToken()
    const config = {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    }
    const resp = await fetch(`${baseUrl}/reward/${doc.id}`, {
      method: 'DELETE',
      ...config,
    })
    if (!resp.ok) throw new Error(`Delete failed: ${resp.statusText}`)
  }

  async function deleteRewards(docs: RewardDocument[]) {
    const ids = docs.map((doc) => doc.id).filter((id): id is number => id !== undefined)
    if (ids.length === 0) return
    await authStore.updateToken()
    const params = new URLSearchParams()
    ids.forEach((id) => params.append('ids', String(id)))
    const config = {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`,
      },
    }
    const resp = await fetch(`${baseUrl}/reward/_bulk?${params.toString()}`, {
      method: 'DELETE',
      ...config,
    })
    if (!resp.ok) throw new Error(`Delete failed: ${resp.statusText}`)
  }

  return {
    downloadReward,
    deleteReward,
    deleteRewards,
  }
})
