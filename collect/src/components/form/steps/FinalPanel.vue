<template>
  <div>
    <div class="text-h4 text-center q-mb-xl">
      {{ t('form.final') }}
    </div>
    <div v-if="collector.info.rewards_message" class="q-mb-xl">
      <div class="text-h5 text-center q-mb-md">
        {{ t('form.final_rewards.title') }}
      </div>
      <p>{{ collector.info.rewards_message?.[locale] }}</p>

      <div v-if="transientRecord" class="row justify-center q-mt-lg">
        <q-btn
          v-if="hasRewards"
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
import type { Record } from 'src/models'
import InfoPanel from 'src/components/form/steps/InfoPanel.vue'

const { t, locale } = useI18n()
const survey = useSurvey()
const collector = useCollector()

const transientRecord = ref<Record | null>(null)

const hasRewards = computed(() => {
  return collector.info?.with_rewards
})

const rewardUrl = computed(() => {
  if (!transientRecord.value?.token) return null

  return `/certificate/${transientRecord.value?.token}`
})

onMounted(() => {
  transientRecord.value = { ...survey.record }
  survey.finish()
})

async function onDownloadReward() {
  if (!transientRecord.value || !transientRecord.value.token) return
  const dateiso = new Date().toISOString().split('T')[0]
  await collector.downloadReward(transientRecord.value, `${t('main.brand')}-${dateiso}`)
}
</script>
