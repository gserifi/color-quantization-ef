import { useState } from "react"
import {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withDelay,
  withSequence,
  runOnUI,
} from "react-native-reanimated"

export const captureAnimation = () => {
  "worklet"
  const progress = useSharedValue(1.0)

  const style = useAnimatedStyle(() => ({
    transform: [{ scale: progress.value }],
  }))

  const trigger = runOnUI(() => {
    return
    progress.value = withSpring(0.9, null, () => {
      progress.value = withSpring(1.1, null, () => {
        progress.value = withSpring(1.0)
      })
    })
  })
  return [style, trigger]
}

export const rotateAnimation = () => {
  "worklet"
  const angle = useSharedValue(0.0)
  const rotationSpring = {
    damping: 10,
    stiffness: 120,
  }

  const trigger = (type) =>
    runOnUI(() => {
      if (type) {
        angle.value = withSpring(Math.PI, rotationSpring)
      } else {
        angle.value = withSpring(2 * Math.PI, rotationSpring, () => (angle.value = 0))
      }
    })()

  const style = useAnimatedStyle(() => ({
    transform: [{ rotate: angle.value }],
  }))

  return [style, trigger]
}
