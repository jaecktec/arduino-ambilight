#include <Arduino.h>
#include <FastLED.h>
#include <CmdBuffer.hpp>
#include <CmdCallback.hpp>
#include <CmdParser.hpp>
#include <ESP8266WiFi.h>
#include <ESPAsyncUDP.h>
#include <pb_decode.h>
#include <pb_encode.h>
#include "proto/z_message.pb.h"

#define LED_PIN 4
#define CHIPSET WS2811
#define NUM_LEDS 104
// #define NUM_LEDS 1
#define BRIGHTNESS 255

AsyncUDP udp;

CRGB leds[NUM_LEDS];
CmdParser myParser;
CmdBuffer<32> myBuffer;
CmdCallback_P<2> myCallback;

void functWPSEnable(CmdParser *myParser);

SetColorMessage message;

void udpPackageHandler(AsyncUDPPacket packet)
{
    message = SetColorMessage_init_zero;
    pb_istream_t stream = pb_istream_from_buffer(packet.data(), packet.length());

    if (!pb_decode(&stream, SetColorMessage_fields, &message))
    {
        Serial.println("message could not be decoded");
    }
    else
    {
        uint8_t idx = 0;
        for (idx = 0; idx < NUM_LEDS; idx++)
        {
            leds[idx].r = message.colors[idx].R;
            leds[idx].g = message.colors[idx].G;
            leds[idx].b = message.colors[idx].B;
        }
        FastLED.setBrightness(message.brightness);
        FastLED.show();
    }
}

void setup()
{
    Serial.begin(115200);
    delay(100);

    FastLED.addLeds<CHIPSET, LED_PIN>(leds, NUM_LEDS).setCorrection(TypicalSMD5050);
    FastLED.setBrightness(BRIGHTNESS);
    myCallback.addCmd(PSTR("WPS"), &functWPSEnable);
    myBuffer.setEcho(true);

    Serial.setDebugOutput(true);
    Serial.printf("[WIFI] try connection to stored SSID '%s'n", WiFi.SSID().c_str());
    WiFi.mode(WIFI_STA);
    WiFi.begin(WiFi.SSID().c_str(), WiFi.psk().c_str());
    uint8_t cnt = 0;
    while ((WiFi.status() == WL_DISCONNECTED) && (cnt < 10))
    {
        delay(500);
        Serial.print(".");
        cnt++;
    }
    wl_status_t Status = WiFi.status();
    if (Status == WL_CONNECTED)
    {
        Serial.printf("[WIFI] Successfully logged in to SSID '%s'-n", WiFi.SSID().c_str());
    }
    else
    {
        Serial.println("[WIFI] could not connect to WiFi from store");
    }

    if (udp.listen(1234))
    {
        Serial.print("UDP Listening on IP: ");
        Serial.println(WiFi.localIP());
        udp.onPacket(udpPackageHandler);
    }

    uint8_t idx = 0;
    for (idx = 0; idx < NUM_LEDS; idx++)
    {
        leds[idx].r = 0;
        leds[idx].g = 0;
        leds[idx].b = 0;
    }
    FastLED.show();
}

void loop()
{
    myCallback.updateCmdProcessing(&myParser, &myBuffer, &Serial);
}

void functWPSEnable(CmdParser *myParser)
{
    Serial.println("[WIFI] Click on your router WPS button...");
    bool wpsSuccess = WiFi.beginWPSConfig();
    if (wpsSuccess)
    {
        //Doesn't always have to be successful! After a timeout, the SSID is empty
        String newSSID = WiFi.SSID();
        if (newSSID.length() > 0)
        {
            //Only when an SSID was found were we successful
            Serial.printf("[WIFI] WPS done. Successfully logged in to SSID '%s'", newSSID.c_str());
        }
        else
        {
            wpsSuccess = false;
        }
    }
    else
    {
        Serial.println("[WIFI] WPS configuration failed");
    }
}