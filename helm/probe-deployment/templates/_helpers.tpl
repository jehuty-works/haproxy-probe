{{/* vim: set filetype=mustache: */}}

{{/*
Generate the IPRM Standard labels necessary for Route and Ingress objects.
Labels will be used to identify which URLs should or should not be scanned 
by vulnerability scanning tools.
*/}}
{{- define "securityCompliance.routeLabels" -}}
{{- if .Values.webScan -}}
iprm.ally.com/enable_scan: {{ .Values.webScan | default "true" }}
{{- end }}
iprm.ally.com/app_id: {{ required ".Values.app_id cannot be empty!" .Values.app_id }}
iprm.ally.com/project: {{ required ".Values.project cannot be empty!" .Values.project }}
iprm.ally.com/env: {{ required ".Values.environment cannot be empty!" .Values.environment }}
{{- end -}}
{{- end -}}

{{/*
Expand the name of the chart.
*/}}
{{- define "redis-probe.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "redis-probe.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "redis-probe.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "redis-probe.labels" -}}
helm.sh/chart: {{ include "redis-probe.chart" . }}
{{ include "redis-probe.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "redis-probe.selectorLabels" -}}
app.kubernetes.io/name: {{ include "redis-probe.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "redis-probe.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "redis-probe.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
