import { Component, OnInit } from '@angular/core';
import { Map, tileLayer } from 'leaflet';

import * as L from 'leaflet';
import * as clusterData200 from '../assets/data.json';
import * as clusterData100 from '../assets/data_todo_100.json';
import * as clusterData75 from '../assets/data_todo_75.json';
import * as clusterData50 from '../assets/data_todo_50.json';
import * as clusterData25 from '../assets/data_todo_25.json';


// const iconRetinaUrl = 'marker-icon-2x.png';
const iconRetinaUrl = 'marker-icon.png';
const iconUrl = 'marker-icon.png';
const shadowUrl = 'marker-shadow.png';
const iconDefault = L.icon({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});
L.Marker.prototype.options.icon = iconDefault;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  title = 'cluster-map';
  map200: Map;
  map100: Map;
  map75: Map;
  map50: Map;
  map25: Map;
  propertyList = [];

  ngOnInit() {

    this.map200 = new Map('map200').setView([40.4169019, -3.7056721], 11);
    tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map200);
    clusterData200.Cluster.forEach((cluster) => {
      L.marker([cluster.latitud, cluster.longitud], { title: `${cluster.id_cluster}` })
        .bindPopup(`<b>${cluster.id_cluster}</b>`)
        .addTo(this.map200)
        .openPopup();
    });

    this.map100 = new Map('map100').setView([40.4169019, -3.7056721], 11);
    tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map100);
    clusterData100.Cluster.forEach((cluster) => {
      L.marker([cluster.latitud, cluster.longitud], { title: `${cluster.id_cluster}` })
        .bindPopup(`<b>${cluster.id_cluster}</b>`)
        .addTo(this.map100)
        .openPopup();
    });

    this.map75 = new Map('map75').setView([40.4169019, -3.7056721], 11);
    tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map75);
    clusterData75.Cluster.forEach((cluster) => {
      L.marker([cluster.latitud, cluster.longitud], { title: `${cluster.id_cluster}` })
        .bindPopup(`<b>${cluster.id_cluster}</b>`)
        .addTo(this.map75)
        .openPopup();
    });

    this.map50 = new Map('map50').setView([40.4169019, -3.7056721], 11);
    tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map50);
    clusterData50.Cluster.forEach((cluster) => {
      L.marker([cluster.latitud, cluster.longitud], { title: `${cluster.id_cluster}` })
        .bindPopup(`<b>${cluster.id_cluster}</b>`)
        .addTo(this.map50)
        .openPopup();
    });

    this.map25 = new Map('map25').setView([40.4169019, -3.7056721], 11);
    tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map25);
    clusterData25.Cluster.forEach((cluster) => {
      L.marker([cluster.latitud, cluster.longitud], { title: `${cluster.id_cluster}` })
        .bindPopup(`<b>${cluster.id_cluster}</b>`)
        .addTo(this.map25)
        .openPopup();
    });


  }
}
