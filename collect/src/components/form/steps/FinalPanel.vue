<template>
  <div>
    <div class="text-h4 text-center q-mb-xl">
      {{ t('form.final') }}
    </div>
    <div v-if="hasRewards && !wasRewarded" class="q-mb-xl">
      <div class="text-h5 text-center q-mb-md">
        {{ t('form.final_rewards.title') }}
      </div>
      <p>{{ collector.info.rewards_message?.[locale] }}</p>

      <div v-if="transientRecord" class="row justify-center q-mt-lg">
        <q-btn
          v-if="withRewards"
          rounded
          no-caps
          color="primary"
          :label="t('form.final_rewards.download_reward')"
          icon-right="download"
          size="lg"
          @click="onDownloadReward"
          :disable="!transientRecord.token"
        />
        <q-btn
          v-else-if="rewardUrl"
          rounded
          no-caps
          color="primary"
          :label="t('form.final_rewards.download_certificate')"
          icon-right="download"
          size="lg"
          :href="rewardUrl"
          target="_blank"
          rel="noopener noreferrer"
        />
      </div>
    </div>
    <InfoPanel />
  </div>
</template>

<script setup lang="ts">
import { Cookies } from 'quasar'
import type { Record } from 'src/models'
import InfoPanel from 'src/components/form/steps/InfoPanel.vue'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()

const transientRecord = ref<Record | null>(null)
const rewardCookieName = ref('')
const wasRewarded = ref(false)

const hasRewards = computed(() => {
  return collector.info.rewards_message
})

const withRewards = computed(() => {
  return collector.info?.with_rewards
})

const rewardUrl = computed(() => {
  if (!transientRecord.value?.token) return null

  return `/certificate/${transientRecord.value?.token}`
})

onMounted(async () => {
  rewardCookieName.value = await survey.getRewardCookieName()
  const cookieValue = await survey.getRewardCookieValuePrefix()
  const rewarded = Cookies.get(rewardCookieName.value)
  if (rewarded && rewarded.startsWith(cookieValue)) {
    wasRewarded.value = true
  }
  transientRecord.value = { ...survey.record }
  survey.finish()
})

async function onDownloadReward() {
  if (wasRewarded.value || !transientRecord.value || !transientRecord.value.token) return
  const dateiso = new Date().toISOString().split('T')[0]
  const prefix = await survey.getRewardCookieValuePrefix()
  Cookies.set(rewardCookieName.value, `${prefix}-${dateiso}`, {
    expires: collector.info.ends_in || 365,
  })
  const baseName = `${t('main.brand')}${dateiso}`
  await collector.downloadReward(transientRecord.value, baseName)
}
</script>
