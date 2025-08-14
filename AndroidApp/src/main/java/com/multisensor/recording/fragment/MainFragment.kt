package com.multisensor.recording.fragment

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import com.multisensor.recording.MainActivity

/**
 * Main Fragment - Device connection status and management
 * Based on IRCamera MainFragment structure
 */
@SuppressLint("NotifyDataSetChanged")
class MainFragment : Fragment(), View.OnClickListener {

    private lateinit var adapter: DeviceAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_main, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        initView()
    }

    private fun initView() {
        adapter = DeviceAdapter()
        view?.findViewById<View>(R.id.tv_connect_device)?.setOnClickListener(this)
        
        adapter.onItemClickListener = { deviceType ->
            // Handle device click - navigate to recording tab
            val activity = activity as? MainActivity
            activity?.navigateToRecording()
        }

        val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())
        recyclerView?.adapter = adapter
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    private fun refresh() {
        // Check if any devices are available (placeholder logic)
        val hasAnyDevice = hasConnectedDevices()
        view?.findViewById<View>(R.id.cl_has_device)?.isVisible = hasAnyDevice
        view?.findViewById<View>(R.id.cl_no_device)?.isVisible = !hasAnyDevice
        adapter.notifyDataSetChanged()
    }

    private fun hasConnectedDevices(): Boolean {
        // Placeholder - in real implementation, check actual device status
        return true // Always show devices for demo
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.tv_connect_device -> {
                // Navigate to device connection or initialize devices
                refresh()
            }
        }
    }

    private class DeviceAdapter : RecyclerView.Adapter<DeviceAdapter.ViewHolder>() {
        
        var onItemClickListener: ((type: DeviceType) -> Unit)? = null

        private val devices = listOf(
            DeviceInfo(DeviceType.RGB_CAMERA, "RGB Camera", true),
            DeviceInfo(DeviceType.THERMAL_CAMERA, "Thermal Camera", true),
            DeviceInfo(DeviceType.GSR_SENSOR, "GSR Sensor", false)
        )

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            return ViewHolder(
                LayoutInflater.from(parent.context).inflate(
                    R.layout.item_device_connect,
                    parent,
                    false
                )
            )
        }

        @SuppressLint("SetTextI18n")
        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val device = devices[position]
            val hasTitle = position == 0

            holder.itemView.findViewById<View>(R.id.tv_title)?.isVisible = hasTitle
            holder.itemView.findViewById<android.widget.TextView>(R.id.tv_title)?.text = "Multi-Sensor Devices"

            val bgView = holder.itemView.findViewById<View>(R.id.iv_bg)
            val nameView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_name)
            val stateView = holder.itemView.findViewById<View>(R.id.view_device_state)
            val stateTextView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_state)
            
            bgView?.isSelected = device.isConnected
            nameView?.isSelected = device.isConnected
            stateView?.isSelected = device.isConnected
            stateTextView?.isSelected = device.isConnected
            
            nameView?.text = device.name
            stateTextView?.text = if (device.isConnected) "online" else "offline"
        }

        override fun getItemCount(): Int = devices.size

        inner class ViewHolder(rootView: View) : RecyclerView.ViewHolder(rootView) {
            init {
                rootView.findViewById<View>(R.id.iv_bg)?.setOnClickListener {
                    val position = adapterPosition
                    if (position != RecyclerView.NO_POSITION) {
                        onItemClickListener?.invoke(devices[position].type)
                    }
                }
            }
        }
    }

    enum class DeviceType {
        RGB_CAMERA,
        THERMAL_CAMERA,
        GSR_SENSOR
    }

    data class DeviceInfo(
        val type: DeviceType,
        val name: String,
        val isConnected: Boolean
    )
}