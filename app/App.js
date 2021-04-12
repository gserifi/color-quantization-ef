import { Buffer } from "buffer"
import GetPixelColor from "react-native-get-pixel-color"

import React, { useState, useEffect, useRef } from "react"
import { StyleSheet, Text, View, StatusBar } from "react-native"
import { Camera } from "expo-camera"
import * as MediaLib from "expo-media-library"
import { RefreshCw as RotateCam, Zap, ZapOff } from "react-native-feather"
import * as Haptics from "expo-haptics"
import Animated from "react-native-reanimated"
import TouchableScale from "react-native-touchable-scale"

import { captureAnimation, rotateAnimation } from "./animations"

const useType = (initialValue = Camera.Constants.Type.back) => {
  const [type, setType] = useState(initialValue)
  const toggle = () => {
    setType(
      type === Camera.Constants.Type.back ? Camera.Constants.Type.front : Camera.Constants.Type.back
    )
  }

  return [type, toggle]
}

const useToggle = (initialValue = false) => {
  const [value, setValue] = useState(initialValue)
  const toggle = () => setValue(!value)
  return [value, toggle]
}

const hapticWrap = (fn) => {
  return (...args) => {
    Haptics.selectionAsync()
    fn(...args)
  }
}

const scaleArgs = {
  tension: 150,
  friction: 2,
}

export default function App() {
  const [permission, setPermission] = useState(null)

  const [type, toggleType] = useType()
  const [flash, toggleFlash] = useToggle(false)

  const camera = useRef(null)

  const [captureStyle, captureTrigger] = captureAnimation()
  const [rotateStyle, rotateTrigger] = rotateAnimation()

  useEffect(() => {
    ;(async () => {
      const { status } = await Camera.requestPermissionsAsync()
      const { status: mediaStatus } = await MediaLib.requestPermissionsAsync()
      setPermission(status === "granted" && mediaStatus === "granted")
    })()
  }, [])

  if (permission === null) {
    return <View />
  }
  if (permission === false) {
    return <Text>No access to camera and/or photo library.</Text>
  }

  const takePicture = async () => {
    await captureTrigger()
    try {
      const { uri, base64 } = await camera.current.takePictureAsync({
        base64: true,
      })
      await GetPixelColor.setImage(uri)
      GetPixelColor.pickColorAt(100, 100).then(console.log)
      const asset = await MediaLib.createAssetAsync(uri)

      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
    } catch (e) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)
      console.log(e)
    }
  }

  const rotateWrap = (fn) => {
    return async (...args) => {
      await rotateTrigger(type === Camera.Constants.Type.back)
      fn(...args)
    }
  }

  return (
    <View style={styles.container}>
      <StatusBar hidden={true} />
      <Camera
        ref={camera}
        style={styles.camera}
        ratio="16:9"
        type={type}
        flashMode={flash ? "on" : "off"}
      >
        <View style={styles.flashControl}>
          <TouchableScale style={styles.save} onPress={hapticWrap(toggleFlash)} {...scaleArgs}>
            {flash ? <Zap stroke="#ffffff" /> : <ZapOff stroke="#ffffff" />}
          </TouchableScale>
        </View>
        <View style={styles.buttonContainer}>
          <View style={{ flex: 1, alignItems: "center", flexDirection: "row" }}>
            <View style={{ flex: 0.2 }} />
            <TouchableScale
              style={styles.captureButton}
              onPress={hapticWrap(takePicture)}
              {...scaleArgs}
            >
              <Animated.View style={[styles.outerRing, captureStyle]}>
                <View style={styles.innerRing}></View>
              </Animated.View>
            </TouchableScale>
            <TouchableScale
              style={styles.flip}
              onPress={rotateWrap(hapticWrap(toggleType))}
              {...scaleArgs}
            >
              <Animated.View style={rotateStyle}>
                <RotateCam stroke="#ffffff" />
              </Animated.View>
            </TouchableScale>
          </View>
        </View>
      </Camera>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
    justifyContent: "space-between",
  },
  flashControl: {
    flex: 1,
    backgroundColor: "transparent",
    alignItems: "flex-end",
    justifyContent: "flex-start",
    padding: 48,
    paddingRight: 24,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "center",
    padding: 64,
  },
  captureButton: {
    flex: 0.6,
    alignItems: "center",
    justifyContent: "center",
  },
  outerRing: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "#ffffff50",
    alignItems: "center",
    justifyContent: "center",
  },
  innerRing: {
    width: 65,
    height: 65,
    borderRadius: 32.5,
    backgroundColor: "#ffffff",
  },
  flip: {
    flex: 0.2,
    justifyContent: "center",
    alignItems: "center",
  },
  save: {
    flex: 0.2,
    alignItems: "flex-end",
  },
  text: {
    fontSize: 18,
    color: "white",
  },
})
