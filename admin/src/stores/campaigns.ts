import { api } from 'src/boot/api'
import type { Campaign, RewardDocuments } from 'src/models'

const services = useServices()
const authStore = useAuthStore()

export const useCampaigns = defineStore('campaigns', () => {
  const items = ref<Campaign[]>([])
  // const company = ref<Company>()
  const companyId = ref<number>()
  const service = services.make('campaign')
  const loading = ref(false)

  async function load() {
    if (companyId.value === undefined) return
    loading.value = true

    return service
      .find({
        $limit: 100,
        filter: {
          company_id: companyId.value,
        },
      })
      .then((res) => {
        items.value = res.data
      })
      .catch(() => {
        items.value = []
      })
      .finally(() => {
        loading.value = false
      })
  }

  async function loadIfNeeded(id: number | undefined | null) {
    if (id === null || id === undefined) return
    if (companyId.value === id && items.value.length > 0) return

    companyId.value = id
    await load()
  }

  async function getRewards(campaign: Campaign): Promise<RewardDocuments | null> {
    if (campaign.id === undefined) return null
    return authStore.updateToken().then(async () => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api
        .get(`/campaign/${campaign.id}/rewards`, config)
        .then((res) => {
          return res.data as RewardDocuments
        })
        .catch(() => {
          return null
        })
    })
  }

  async function upload_rewards(campaign: Campaign, files: Blob[]): Promise<boolean> {
    if (campaign.id === undefined) return false
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (file) {
        formData.append('files', file)
      }
    }
    return authStore.updateToken().then(async () => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
          'Content-Type': 'multipart/form-data',
        },
      }
      return api
        .post(`/campaign/${campaign.id}/rewards/_upload`, formData, config)
        .then(() => {
          return true
        })
        .catch(() => {
          return false
        })
    })
  }

  return {
    items,
    companyId,
    loading,
    service,
    load,
    loadIfNeeded,
    getRewards,
    upload_rewards,
  }
})
