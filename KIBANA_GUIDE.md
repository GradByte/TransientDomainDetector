# Kibana Dashboard Guide

Step-by-step guide to view your transient domain detection results in Kibana.

## 📊 Quick Access

**Kibana URL**: http://localhost:5601

---

## Step 1: Create Index Pattern

Before you can view data, you need to create an index pattern to tell Kibana where to find your data.

1. **Open Kibana**: http://localhost:5601

2. **Navigate to Index Patterns**:
   - Click the **☰ menu** (hamburger icon) in the top-left
   - Scroll down to **Management** section
   - Click **Stack Management**
   - In the left sidebar, under **Kibana**, click **Data Views** (or **Index Patterns**)

3. **Create Index Pattern**:
   - Click **Create data view** button
   - **Name**: `Transient Domains`
   - **Index pattern**: `transient-domains*`
   - **Timestamp field**: Select `processed_timestamp`
   - Click **Save data view to Kibana**

✅ Your index pattern is now created!

---

## Step 2: View Data in Discover

Now you can explore your data:

1. **Navigate to Discover**:
   - Click the **☰ menu** in the top-left
   - Under **Analytics**, click **Discover**

2. **Select Your Data View**:
   - In the top-left dropdown, select **Transient Domains**
   - You should now see your domain data!

3. **What You'll See**:
   - Timeline of detections over time
   - Table with all detected domains
   - Fields on the left sidebar

4. **Useful Actions**:
   - **Filter by prediction**: Click on `prediction` field → `malicious` to see only malicious domains
   - **Adjust time range**: Use the time picker in the top-right
   - **Add columns**: Click `+` next to fields like `domain`, `confidence`, `prediction`
   - **Search**: Use the search bar to find specific domains

---

## Step 3: Create Visualizations

### Visualization 1: Pie Chart - Benign vs Malicious

1. **Navigate to Visualize**:
   - Click **☰ menu** → **Analytics** → **Visualizations**
   - Click **Create visualization**

2. **Select Visualization Type**:
   - Choose **Pie** or **Donut**

3. **Configure**:
   - **Data view**: Select `Transient Domains`
   - **Slice by**: Click **Add field** → Select `prediction.keyword`
   - **Metrics**: Should show `Count` by default

4. **Save**:
   - Click **Save** in the top-right
   - Name: `Benign vs Malicious Distribution`

---

### Visualization 2: Bar Chart - Top Malicious Domains

1. **Create new visualization**:
   - Choose **Bar** (horizontal)

2. **Configure**:
   - **Data view**: `Transient Domains`
   - **Metrics**: Count
   - **Breakdown**: `domain.keyword`
   - **Add filter**: Click **Add filter** → `prediction is malicious`
   - **Number of values**: Change to 20

3. **Save**:
   - Name: `Top 20 Malicious Domains`

---

### Visualization 3: Line Chart - Detections Over Time

1. **Create new visualization**:
   - Choose **Line**

2. **Configure**:
   - **Metrics**: Count
   - **Horizontal axis**: `processed_timestamp` (Date Histogram)
   - **Breakdown**: `prediction.keyword`

3. **Save**:
   - Name: `Detections Timeline`

---

### Visualization 4: Data Table - Recent Detections

1. **Create new visualization**:
   - Choose **Table**

2. **Configure**:
   - **Rows**: Add multiple fields:
     - `domain.keyword`
     - `prediction.keyword`
     - `confidence`
     - `processed_timestamp`
   - **Sort by**: `processed_timestamp` (descending)

3. **Save**:
   - Name: `Recent Detections Table`

---

## Step 4: Create Dashboard

Now combine all visualizations into one dashboard:

1. **Navigate to Dashboard**:
   - Click **☰ menu** → **Analytics** → **Dashboard**
   - Click **Create dashboard**

2. **Add Visualizations**:
   - Click **Add from library**
   - Select all the visualizations you created:
     - Benign vs Malicious Distribution
     - Top 20 Malicious Domains
     - Detections Timeline
     - Recent Detections Table
   - Arrange them on the dashboard by dragging

3. **Customize Layout**:
   - Resize visualizations by dragging corners
   - Suggested layout:
     ```
     ┌─────────────────────────────────────────┐
     │  Benign vs Malicious (Pie)    │ Stats  │
     ├─────────────────────────────────────────┤
     │  Detections Timeline (Line Chart)       │
     ├─────────────────────────────────────────┤
     │  Top Malicious Domains (Bar Chart)      │
     ├─────────────────────────────────────────┤
     │  Recent Detections Table                │
     └─────────────────────────────────────────┘
     ```

4. **Save Dashboard**:
   - Click **Save** in top-right
   - Name: `Transient Domain Detection Dashboard`

---

## Step 5: Add Filters and Controls

Make your dashboard interactive:

1. **On your dashboard**, click **Edit**

2. **Add Controls**:
   - Click **Controls** → **Add control**
   - **Options list**: Select `prediction.keyword`
   - This adds a filter dropdown
   - Click **Save and return**

3. **Add Time Range Controls**:
   - Use the time picker in top-right to filter by time range
   - Options: Last 15 minutes, Last hour, Last 24 hours, etc.

---

## 📊 Example Queries in Discover

Try these searches in the Discover search bar:

### Find All Malicious Domains
```
prediction: "malicious"
```

### High Confidence Malicious Domains (>95%)
```
prediction: "malicious" AND confidence > 0.95
```

### Domains with Numbers
```
domain: *[0-9]*
```

### Long Domains (>50 characters)
```
features.DomainLength > 50
```

### Recent High-Risk Detections (Last Hour)
```
prediction: "malicious" AND confidence > 0.9
```
(Then set time range to "Last 1 hour" in time picker)

---

## 🔍 Viewing Specific Domain Details

To see all details for a specific domain:

1. In **Discover**, find the domain in the table
2. Click the **>** arrow next to the domain entry
3. This expands to show all fields:
   - Domain name
   - Prediction and confidence
   - All features (DomainLength, NumericRatio, etc.)
   - Timestamps
   - Certificate info

---

## 📈 Creating Alerts (Optional)

Set up alerts for malicious domains:

1. **Navigate to Alerting**:
   - **☰ menu** → **Management** → **Stack Management**
   - Under **Alerts and Insights**, click **Rules and Connectors**

2. **Create Rule**:
   - Click **Create rule**
   - **Name**: `High Confidence Malicious Domain Alert`
   - **Rule type**: Select **Elasticsearch query**
   - **Index**: `transient-domains*`
   - **Query**: 
     ```json
     {
       "query": {
         "bool": {
           "must": [
             {"term": {"prediction": "malicious"}},
             {"range": {"confidence": {"gte": 0.95}}}
           ]
         }
       }
     }
     ```
   - **Check every**: 1 minute
   - **Actions**: Configure email/Slack notification

---

## 💡 Tips

### Performance
- If you have lots of data, use time filters to narrow results
- Use saved searches for common queries

### Sharing
- Share dashboard with team: Click **Share** → **Get links**
- Export visualizations as CSV: In table visualizations, click **⋮** → **Download CSV**

### Refresh
- Enable auto-refresh: Click the refresh icon in top-right → Set interval (e.g., 30s)
- Useful for live monitoring during detection runs

---

## 🎯 Quick Links

After setup, bookmark these:

- **Main Dashboard**: http://localhost:5601/app/dashboards
- **Discover**: http://localhost:5601/app/discover
- **Visualizations**: http://localhost:5601/app/visualize

---

## ❓ Troubleshooting

### No data showing
- Check time range (expand to "Last 7 days" or "Last 30 days")
- Verify data exists: `curl http://localhost:9200/transient-domains/_count`
- Refresh the data view: **Stack Management** → **Data Views** → Click refresh icon

### Visualizations not loading
- Refresh the page
- Check Elasticsearch is running: `docker ps`
- Check browser console for errors

### Can't find fields
- Refresh field list: In Discover, click refresh icon next to field list
- Re-index data view: **Stack Management** → **Data Views** → Select view → **Refresh field list**

---

**Need more help?** Check the [Kibana documentation](https://www.elastic.co/guide/en/kibana/8.11/index.html)
